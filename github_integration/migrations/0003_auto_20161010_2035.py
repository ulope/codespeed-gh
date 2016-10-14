# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import datetime
import enumfields.fields


class JobStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'
    FAILURE = 'failure'


class TargetType(Enum):
    BRANCH = 'branch'
    PR = 'pr'


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0002_auto_20161010_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='commit',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 10, 20, 35, 27, 471475)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='run',
            name='status',
            field=enumfields.fields.EnumField(max_length=10, default='pending', enum=JobStatus),
        ),
        migrations.AlterField(
            model_name='target',
            name='type',
            field=enumfields.fields.EnumField(max_length=10, enum=TargetType),
        ),
    ]
