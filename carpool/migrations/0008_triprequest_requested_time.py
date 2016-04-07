# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0007_trip_trip_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='triprequest',
            name='requested_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 7, 1, 47, 40, 125853, tzinfo=utc), blank=True),
            preserve_default=False,
        ),
    ]
