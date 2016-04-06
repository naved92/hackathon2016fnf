# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0002_auto_20160406_0521'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='driver_NID',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_NID',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
