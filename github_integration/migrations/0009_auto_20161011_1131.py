# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import enumfields.fields


class CommitStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'
    FAILURE = 'failure'


class JobRunStatus(Enum):
    PREPARING = 'preparing'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    KILLED = 'killed'


class TargetType(Enum):
    BRANCH = 'branch'
    PR = 'pr'


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0008_auto_20161011_0956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='status',
        ),
        migrations.AddField(
            model_name='commit',
            name='status',
            field=enumfields.fields.EnumField(max_length=10, default='pending', enum=CommitStatus),
        ),
        migrations.AlterField(
            model_name='job',
            name='run_status',
            field=enumfields.fields.EnumField(max_length=10, default='preparing', enum=JobRunStatus),
        ),
        migrations.AlterField(
            model_name='target',
            name='type',
            field=enumfields.fields.EnumField(max_length=10, enum=TargetType),
        ),
    ]
