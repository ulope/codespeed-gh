import codecs
import json
import subprocess
from contextlib import contextmanager
from enum import Enum
from logging import getLogger
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, IntegerField, TextField
from django.db.models.fields.related import ForeignKey
from enumfields.fields import EnumField

from codespeed.models import Project, Branch
from codespeed.results import save_result, create_report_if_enough_data


log = getLogger(__name__)


GITHUB_HTML_BASE = "https://github.com/{s.repo_name}"
GITHUB_HTML_PR = "%s/pull/{s.pr_number}" % (GITHUB_HTML_BASE, )
GITHUB_HTML_TREE = "%s/tree/{s.branch_name}" % (GITHUB_HTML_BASE, )
GITHUB_API_CONTENTS = "https://api.github.com/repos/{s.target.repo_name}/contents/{path}?ref={s.sha}"


class CloneError(Exception):
    def __init__(self, repo, output):
        self.repo = repo
        self.output = output

    def __str__(self):
        return "Error cloning repo '{s.repo}':\n{s.output}".format(s=self)


class TargetType(Enum):
    BRANCH = 'branch'
    PR = 'pr'


class Target(Model):
    repo_name = CharField(max_length=500)
    type = EnumField(TargetType)
    pr_number = IntegerField(blank=True, null=True)
    branch_name = CharField(max_length=1000, blank=True, null=True)
    project = ForeignKey('codespeed.Project', blank=True, null=True, related_name='targets')

    class Meta:
        unique_together = ('repo_name', 'pr_number', 'branch_name')

    def get_absolute_url(self):
        if self.type is TargetType.PR:
            return reverse('target_status', kwargs={'repo_name': self.repo_name, 'pr_number': self.pr_number})

    @property
    def is_pr(self):
        return self.type is TargetType.PR

    @property
    def url(self):
        if type is TargetType.BRANCH:
            return GITHUB_HTML_TREE.format(s=self)
        else:
            return GITHUB_HTML_PR.format(s=self)

    @property
    def ref(self):
        if self.type is TargetType.BRANCH:
            return "{s.repo_name}/{s.branch_name}".format(s=self)
        else:
            return "{s.repo_name}#{s.pr_number}".format(s=self)

    def __str__(self):
        return self.ref

    def ensure_project(self):
        if not self.project:
            self.project, _ = Project.objects.get_or_create(
                name=self.repo_name,
                repo_type=Project.GITHUB,
                repo_path=GITHUB_HTML_BASE.format(s=self)
            )
            self.save()
        return self.project


class CommitStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'
    FAILURE = 'failure'


class Commit(Model):
    target = ForeignKey(Target, related_name='commits')
    sha = CharField(max_length=40, db_index=True)
    date = DateTimeField()
    status = EnumField(CommitStatus, default=CommitStatus.PENDING)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return "{s.target}: {s.short_sha}: {s.status}".format(s=self)

    @property
    def short_sha(self):
        return self.sha[:8]

    def save(self, *args, **kwargs):
        from github_integration.utils import set_commit_status

        if self.target and self.target.type is TargetType.PR:
            set_commit_status(self)
        super(Commit, self).save(*args, **kwargs)

    def get_file(self, path):
        resp = requests.get(GITHUB_API_CONTENTS.format(s=self, path=path))
        if not 199 < resp.status_code < 300:
            return
        content = resp.json()
        if 'content' not in content:
            return
        return codecs.decode(
            content['content'].encode("ascii"),
            'base64'
        )

    @contextmanager
    def clone(self):
        with TemporaryDirectory(dir=settings.TMP_DIR) as tmp_dir:
            log.debug("Cloning %s into %s", self, tmp_dir)
            repo_url = "https://{token}@github.com/{s.target.repo_name}.git".format(
                token=settings.GITHUB_TOKEN,
                s=self
            )
            clone_log = []
            try:
                clone_log.append(subprocess.check_output(["git", "init"], stderr=subprocess.STDOUT, cwd=tmp_dir))
                clone_log.append(subprocess.check_output(["git", "remote", "add", "origin", repo_url], stderr=subprocess.STDOUT, cwd=tmp_dir))
                clone_log.append(subprocess.check_output(["git", "fetch", "origin"], stderr=subprocess.STDOUT, cwd=tmp_dir))
                clone_log.append(subprocess.check_output(["git", "checkout", "-q", self.sha], stderr=subprocess.STDOUT, cwd=tmp_dir))
                # Remove remote to avoid leaking credentials
                clone_log.append(subprocess.check_output(["git", "remote", "remove", "origin"], stderr=subprocess.STDOUT, cwd=tmp_dir))
            except CalledProcessError as ex:
                clone_log.append(ex.output)
                raise CloneError(self.target.repo_name, "\n".join(clone_log)) from ex
            yield tmp_dir


class JobStatus(Enum):
    PREPARING = 'preparing'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    ERROR = 'error'
    TIMEOUT = 'timeout'


class Job(Model):
    name = CharField(max_length=500)
    commit = ForeignKey(Commit, related_name='jobs')
    status = EnumField(JobStatus, default=JobStatus.PREPARING)
    log = TextField(blank=True, null=True)
    result = TextField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'commit')
        ordering = ('name', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)
        self.update_codespeed()

    def update_codespeed(self):
        if self.status is JobStatus.SUCCESS and self.result:
            if getattr(self, '_codespeed_updated', False):
                # Prevent duplicate updates
                return
            log.debug("Updating codespeed results")
            project_name = self.commit.target.ensure_project().name
            if self.commit.target.type is TargetType.BRANCH:
                branch_name = self.commit.target.branch_name
                if branch_name == 'master':
                    branch_name = 'default'
            else:
                branch_name = "pr-{}".format(self.commit.target.pr_number)
            rev = None
            for test, result in json.loads(self.result).items():
                (rev, exe, env), err = save_result(
                    dict(
                        environment='default',
                        project=project_name,
                        units='us',
                        executable=self.name,
                        branch=branch_name,
                        commitid=self.commit.sha,
                        revision_date=self.commit.date,
                        benchmark=test,
                        result_value=result['mean'],
                        min=result['min'],
                        max=result['max'],
                        std_dev=result['stdev']
                    )
                )
            self._codespeed_updated = True
            if rev:
                base_branch = None
                if self.commit.target.is_pr:
                    # For PRs create a report against the base branch
                    try:
                        base_branch = Branch.objects.get(project=rev.project, name=settings.DEF_BRANCH)
                    except Branch.DoesNotExist:
                        pass
                return create_report_if_enough_data(rev, exe, env, base_branch=base_branch)
