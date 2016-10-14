from tarfile import TarFile

import requests
from django.conf import settings
from django.utils import timezone
from django_rq.decorators import job
from io import BytesIO

from github_integration.models import Target, TargetType, Commit, CommitStatus


COMMIT_STATUS_URL = (
    "https://api.github.com/repos/{repo_name}/statuses/{commit_sha}"
    "?client_id={client_id}&client_secret={client_secret}"
)


def set_commit_status(commit, message=None):
    if not message:
        message = "Codespeed: {}".format(commit.status.value)
    _set_commit_status.delay(
        commit.target.repo_name,
        commit.sha,
        commit.status.value,
        message,
        commit.target.get_absolute_url()
    )


@job
def _set_commit_status(repo_name, commit_sha, state, message, target_url):
    requests.post(
        COMMIT_STATUS_URL.format(
            repo_name=repo_name,
            commit_sha=commit_sha,
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
        ),
        json={
            'state': state,
            'target_url': settings.BASE_URL.format(target_url),
            'description': message,
            'context': 'codespeed'
        },
        headers={'Authorization': 'token {}'.format(settings.GITHUB_TOKEN)},
    )


def get_target_commit(event_data):
    if 'pull_request' in event_data:
        target, _ = Target.objects.get_or_create(
            repo_name=event_data['pull_request']['head']['repo']['full_name'],
            pr_number=event_data['pull_request']['number'],
            type=TargetType.PR
        )
        commit, _ = Commit.objects.get_or_create(
            target=target,
            sha=event_data['pull_request']['head']['sha'],
            defaults={
                'date': timezone.now()
            }
        )
    else:
        target, _ = Target.objects.get_or_create(
            repo_name=event_data['repository']['full_name'],
            branch_name=event_data['ref'].replace("refs/heads/", ""),
            type=TargetType.BRANCH
        )
        commit, _ = Commit.objects.get_or_create(
            target=target,
            sha=event_data['head_commit']['id'],
            defaults={
                'date': event_data['head_commit']['timestamp']
            }
        )
    return target, commit


def get_file_contents_from_tar_stream(tar_stream):
    if not tar_stream:
        return
    fp = BytesIO(tar_stream)
    tar_file = TarFile(fileobj=fp)
    file = tar_file.extractfile(tar_file.next())
    if file:
        return file.read().decode("UTF-8")
