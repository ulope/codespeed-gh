# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0006_job_run_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='log',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='result',
            field=models.TextField(null=True, blank=True),
        ),
    ]
