# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import github_integration.models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0003_auto_20161010_2035'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Run',
            new_name='Job'
        ),
        migrations.AlterModelOptions(
            name='commit',
            options={'ordering': ('-date',)},
        ),
    ]
