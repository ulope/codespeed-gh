# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('github_integration', '0007_auto_20161011_0949'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='job',
            name='commit',
            field=models.ForeignKey(related_name='jobs', to='github_integration.Commit'),
        ),
        migrations.AlterUniqueTogether(
            name='job',
            unique_together=set([('name', 'commit')]),
        ),
    ]
