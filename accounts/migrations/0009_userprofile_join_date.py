# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 23:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20170507_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='join_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]