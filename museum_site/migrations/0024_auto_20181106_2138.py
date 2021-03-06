# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-06 21:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0023_auto_20181024_0251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alias',
            options={'ordering': ['alias']},
        ),
        migrations.AddField(
            model_name='file',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='file',
            name='publish_date',
            field=models.DateField(auto_now_add=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
