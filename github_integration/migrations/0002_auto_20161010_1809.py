# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import migrations, models
import enumfields.fields


class TargetType(Enum):
    BRANCH = 'branch'
    PR = 'pr'


class RunStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    ERROR = 'error'
    FAILURE = 'failure'


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('sha', models.CharField(max_length=40, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('repo_name', models.CharField(max_length=500)),
                ('type', enumfields.fields.EnumField(enum=TargetType, max_length=10)),
                ('pr_number', models.IntegerField(blank=True, null=True)),
                ('branch_name', models.CharField(max_length=1000, blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='run',
            name='repo_name',
        ),
        migrations.RemoveField(
            model_name='run',
            name='sha',
        ),
        migrations.AlterField(
            model_name='run',
            name='status',
            field=enumfields.fields.EnumField(RunStatus, default='pending', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='target',
            unique_together=set([('repo_name', 'pr_number', 'branch_name')]),
        ),
        migrations.AddField(
            model_name='commit',
            name='target',
            field=models.ForeignKey(to='github_integration.Target', related_name='commits'),
        ),
        migrations.AddField(
            model_name='run',
            name='commit',
            field=models.ForeignKey(to='github_integration.Commit', default=0, related_name='runs'),
            preserve_default=False,
        ),
    ]
