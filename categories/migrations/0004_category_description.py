# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-03 01:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(blank=True, max_length=140, null=True),
        ),
    ]
