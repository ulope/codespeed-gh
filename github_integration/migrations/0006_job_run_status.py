# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import enumfields.fields


class JobRunStatus(Enum):
    PREPARING = 'preparing'
    RUNNING = 'running'
    EXITED = 'exited'
    KILLED = 'killed'


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0005_job_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='run_status',
            field=enumfields.fields.EnumField(max_length=10, enum=JobRunStatus, default='preparing'),
        ),
    ]
