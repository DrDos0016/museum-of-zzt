# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-28 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comic', '0004_auto_20170128_0329'),
    ]

    operations = [
        migrations.AddField(
            model_name='comic',
            name='commentary',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
