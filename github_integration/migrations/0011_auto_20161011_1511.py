# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import github_integration.models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('codespeed', '0002_median'),
        ('github_integration', '0010_auto_20161011_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='project',
            field=models.ForeignKey(related_name='targets', null=True, to='codespeed.Project', blank=True),
        ),
        migrations.AlterField(
            model_name='commit',
            name='status',
            field=enumfields.fields.EnumField(enum=github_integration.models.CommitStatus, max_length=10, default='pending'),
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=enumfields.fields.EnumField(enum=github_integration.models.JobStatus, max_length=10, default='preparing'),
        ),
        migrations.AlterField(
            model_name='target',
            name='type',
            field=enumfields.fields.EnumField(enum=github_integration.models.TargetType, max_length=10),
        ),
    ]
