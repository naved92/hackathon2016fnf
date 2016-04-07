# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0005_auto_20160406_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating_event', models.CharField(default=b'R', max_length=5, choices=[(b'R', b'Rating'), (b'CT', b'Create Trip'), (b'ST', b'Share Trip'), (b'P', b'Posting')])),
                ('rating_event_id', models.IntegerField(null=True)),
                ('earned_rating', models.IntegerField(null=True)),
                ('rated_by_user', models.ForeignKey(related_name='rated_by_user', to='carpool.UserProfile')),
                ('rated_user', models.ForeignKey(related_name='rated_user', to='carpool.UserProfile')),
            ],
        ),
    ]
