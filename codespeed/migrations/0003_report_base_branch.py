# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codespeed', '0002_median'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='base_branch',
            field=models.ForeignKey(to='codespeed.Branch', null=True, related_name='fork_reports', blank=True),
        ),
    ]
