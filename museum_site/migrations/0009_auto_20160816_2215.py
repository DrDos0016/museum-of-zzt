# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-16 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0008_article_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='article_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='css',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='file',
            name='company',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AlterField(
            model_name='file',
            name='genre',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
    ]
