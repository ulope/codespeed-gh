# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import enumfields.fields


class JobStatus(Enum):
    PREPARING = 'preparing'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    KILLED = 'killed'


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0009_auto_20161011_1131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='run_status',
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=enumfields.fields.EnumField(default='preparing', max_length=10, enum=JobStatus),
        ),
    ]
