# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codespeed', '0004_auto_20161013_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='average_change',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
