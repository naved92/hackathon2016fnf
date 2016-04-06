# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0004_trip_car_of_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='created_by',
            field=models.ForeignKey(related_name='userprofile', default=1, to='carpool.UserProfile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triprequest',
            name='trip_status',
            field=models.CharField(default=b'p', max_length=2, choices=[(b'a', b'approved'), (b'd', b'disapproved'), (b'o', b'other'), (b'p', b'pending'), (b's', b'suspended')]),
        ),
    ]
