# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_time', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_text', models.CharField(max_length=300, blank=True)),
                ('post_photo', models.ImageField(upload_to=b'post_images/', blank=True)),
                ('post_time', models.DateTimeField(null=True, blank=True)),
                ('post_sharecount', models.IntegerField(null=True, blank=True)),
                ('post_location', models.ForeignKey(blank=True, to='carpool.Location', null=True)),
            ],
            options={
                'ordering': ['-post_time'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='about_me',
            field=models.CharField(max_length=300, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_location',
            field=models.CharField(max_length=300, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(upload_to=b'profile_images', blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='post_maker',
            field=models.ForeignKey(to='carpool.UserProfile'),
        ),
        migrations.AddField(
            model_name='post',
            name='post_sharedfrom',
            field=models.ForeignKey(blank=True, to='carpool.Post', null=True),
        ),
        migrations.AddField(
            model_name='block',
            name='blocked',
            field=models.ForeignKey(related_name='user_who_got_blocked', to='carpool.UserProfile'),
        ),
        migrations.AddField(
            model_name='block',
            name='blocker',
            field=models.ForeignKey(related_name='user_who_blocked', to='carpool.UserProfile'),
        ),
    ]
