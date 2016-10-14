from collections import OrderedDict
from functools import lru_cache
from logging import getLogger
from operator import itemgetter
from tempfile import NamedTemporaryFile

import time
import yaml
from django.conf import settings
from django.db.models import Q
from django_rq.decorators import job
from docker.client import Client
from os.path import realpath

from requests.exceptions import ReadTimeout
from yaml.parser import ParserError

from github_integration.models import Job, CommitStatus, JobStatus, Commit, CloneError, TargetType
from github_integration.utils import get_file_contents_from_tar_stream


log = getLogger(__name__)


@job('jobs')
def run_jobs(commit_id):
    # Allow a few seconds for all webhooks to arrive
    time.sleep(5)
    # For PRs two webhooks are fired, one for the push to the branch and one for the PR itself
    # we're only interested in the PR so we skip the other.
    commit = Commit.objects.get(pk=commit_id)
    log.debug("Processing commit %s", commit)
    if commit.target.type is TargetType.BRANCH:
        pr_commit = Commit.objects.filter(~Q(pk=commit.pk), sha=commit.sha, target__type=TargetType.PR).first()
        if pr_commit:
            # A commit with the same sha pointing to a PR exists - delete this one.
            log.info("Skipping build for commit '%s' for branch '%s' with matching PR #%s",
                     commit, commit.target.branch_name, pr_commit.target.pr_number)
            commit.delete()
            return
    runner = DockerRunner(commit)
    runner.run()


class DockerRunner:
    def __init__(self, commit):
        self.commit = commit

    @property
    @lru_cache(maxsize=1)
    def config(self):
        config_file = self.commit.get_file('.codespeed.yml')
        if not config_file:
            log.warn("No config file found for {s.commit}.".format(s=self))
            return
        config = yaml.safe_load(config_file)
        job_defaults = config.get('defaults', {}).get('job', {})
        jobs = OrderedDict()
        for name, job in sorted(config.get('jobs', {}).items(), key=itemgetter(0)):
            jobs[name] = job_defaults.copy()
            jobs[name].update(job)
            jobs[name]['commands'] = ("\n".join(jobs[name].get('commands', ''))).encode("UTF-8")
        return dict(
            jobs=jobs
        )

    def run(self):
        # Ensure the codespeed 'Project' is available
        self.commit.target.ensure_project()
        if self.commit.status is not CommitStatus.PENDING:
            self.commit.status = CommitStatus.PENDING
            self.commit.save()
        docker = Client()
        try:
            config = self.config
        except ParserError:
            self.commit.status = CommitStatus.ERROR
            self.commit.save()
            return

        jobs = {}
        for job_name in config['jobs'].keys():
            # Precreate Job objects to fill state view
            job, _ = Job.objects.get_or_create(name=job_name, commit=self.commit)
            jobs[job_name] = job

        reports = []
        for job_name, job_definition in config['jobs'].items():
            job = jobs[job_name]
            try:
                with NamedTemporaryFile(dir=settings.TMP_DIR) as commands_file, self.commit.clone() as clone:
                    commands_file.write(b"set +x\nset +e\ncd /code\n")
                    commands_file.write(job_definition['commands'])
                    commands_file.write(b"\n")
                    commands_file.flush()
                    log.debug("Wrote commands to %s", commands_file.name)
                    log.debug("Pulling image %s", job_definition['image'])
                    pull_res = docker.pull(*job_definition['image'].strip().split(":", maxsplit=1))
                    log.debug("Image pulled: %s", pull_res)
                    container = docker.create_container(
                        image=job_definition['image'].strip(),
                        command="/bin/bash /_run_codespeed.sh",
                        volumes=[
                            "/_run_codespeed.sh",
                            "/code"
                        ],
                        environment={
                            'CI': "1",
                            'CODESPEED': "1",
                            'JOB': job_name
                        },
                        host_config=docker.create_host_config(
                            binds={
                                realpath(commands_file.name): {
                                    'bind': "/_run_codespeed.sh",
                                    'mode': 'ro'
                                },
                                realpath(clone): {
                                    'bind': "/code",
                                    'mode': 'rw'
                                }
                            }
                        )
                    )
                    container = container['Id']
                    log.debug("Starting container %s", container)
                    try:
                        docker.start(container)
                        job.status = JobStatus.RUNNING
                        job.save()
                        try:
                            exit_code = docker.wait(container, timeout=600)
                            log.debug("Container %s exited with code %d.", container, exit_code)
                            if exit_code == 0:
                                tar_stream, stat = docker.get_archive(container, job_definition['results_file'])
                                job.result = get_file_contents_from_tar_stream(tar_stream.data)
                                if job.result:
                                    log.debug("Result from container %s succesfully stored", container)
                                    job.status = JobStatus.SUCCESS
                                else:
                                    log.warning("No result from container %s", container)
                                    job.status = JobStatus.ERROR
                            else:
                                job.status = JobStatus.FAILURE
                        except ReadTimeout:
                            log.error("Container %s exceeded timeout. Killing.", container)
                            docker.kill(container)
                            job.status = JobStatus.TIMEOUT
                        job.log = docker.logs(container)
                        reports.append(job.update_codespeed())
                        job.save()
                    finally:
                        docker.remove_container(container)
                        log.debug("Removed container %s", container)
            except CloneError as ex:
                job.status = JobStatus.FAILURE
                job.log = ex.output
                job.save()
        log.debug("Report colors: %s", set(r.colorcode for r in reports if r))
        job_statuses = {j.status for j in self.commit.jobs.all()}
        if JobStatus.TIMEOUT in job_statuses or JobStatus.ERROR in job_statuses:
            self.commit.status = CommitStatus.ERROR
        elif JobStatus.FAILURE in job_statuses:
            self.commit.status = CommitStatus.FAILURE
        else:
            self.commit.status = CommitStatus.SUCCESS
        self.commit.save()
