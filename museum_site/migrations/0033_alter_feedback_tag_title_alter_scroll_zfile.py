# Generated by Django 4.2.14 on 2024-11-23 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0032_series_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback_tag',
            name='title',
            field=models.CharField(choices=[('Bug Report', 'Bug Report'), ('Changelog', 'Changelog'), ('Content Warning', 'Content Warning'), ('Hints and Solutions', 'Hints and Solutions'), ('Review', 'Review'), ('Table of Contents', 'Table of Contents')], max_length=25),
        ),
        migrations.AlterField(
            model_name='scroll',
            name='zfile',
            field=models.ForeignKey(blank=True, help_text='Will try to use key in source URL if blank', null=True, on_delete=django.db.models.deletion.SET_NULL, to='museum_site.file'),
        ),
    ]
