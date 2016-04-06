# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0003_auto_20160406_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='car_of_trip',
            field=models.ForeignKey(default=1234, to='carpool.Car'),
            preserve_default=False,
        ),
    ]
