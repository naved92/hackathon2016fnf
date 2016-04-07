# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0006_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='trip_status',
            field=models.CharField(default=b'p', max_length=2, choices=[(b'a', b'approved'), (b'd', b'disapproved'), (b'o', b'other'), (b'p', b'pending'), (b's', b'suspended'), (b'c', b'completed')]),
        ),
    ]
