# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import enumfields.fields


class RunStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'
    FAILURE = 'failure'


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('repo_name', models.CharField(max_length=500)),
                ('sha', models.CharField(max_length=100)),
                ('status', enumfields.fields.EnumField(default='pending', max_length=10, enum=RunStatus)),
            ],
        ),
    ]
