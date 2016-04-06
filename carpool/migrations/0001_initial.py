# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registration_number', models.CharField(max_length=300, null=True, blank=True)),
                ('car_model', models.CharField(max_length=300, null=True, blank=True)),
                ('number_of_seats', models.IntegerField(null=True, blank=True)),
                ('car_availablity_status', models.CharField(default=b'p', max_length=2, choices=[(b'a', b'active'), (b'd', b'deactive'), (b'o', b'other'), (b'p', b'pending'), (b's', b'suspended')])),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('driver_name', models.CharField(max_length=50, null=True, blank=True)),
                ('driver_address', models.CharField(max_length=300, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location_name', models.CharField(max_length=300, blank=True)),
                ('location_lat', models.FloatField(null=True, blank=True)),
                ('location_long', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_time', models.DateTimeField(blank=True)),
                ('destination', models.ForeignKey(related_name='destination', to='carpool.Location')),
                ('driver_of_trip', models.ForeignKey(to='carpool.Driver')),
                ('source', models.ForeignKey(related_name='source', to='carpool.Location')),
            ],
        ),
        migrations.CreateModel(
            name='TripRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_requested', models.ForeignKey(to='carpool.Trip')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pw', models.CharField(max_length=10, blank=True)),
                ('reward', models.IntegerField(null=True, blank=True)),
                ('address', models.CharField(max_length=300, blank=True)),
                ('verification_status', models.CharField(default=b'p', max_length=2, choices=[(b'a', b'active'), (b'd', b'deactive'), (b'o', b'other'), (b'p', b'pending'), (b's', b'suspended')])),
                ('verification_code', models.CharField(default=b'123456', max_length=128)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='triprequest',
            name='user_requested',
            field=models.ForeignKey(to='carpool.UserProfile'),
        ),
        migrations.AddField(
            model_name='ride',
            name='rider',
            field=models.ForeignKey(to='carpool.UserProfile'),
        ),
        migrations.AddField(
            model_name='ride',
            name='trip',
            field=models.ForeignKey(to='carpool.Trip'),
        ),
        migrations.AddField(
            model_name='driver',
            name='driver_employer',
            field=models.ForeignKey(to='carpool.UserProfile'),
        ),
        migrations.AddField(
            model_name='car',
            name='owner',
            field=models.ForeignKey(to='carpool.UserProfile'),
        ),
    ]
