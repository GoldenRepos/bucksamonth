# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-20 02:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='emoji',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
