# Generated by Django 5.2.1 on 2025-07-10 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0036_file_year_alter_file_release_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='download',
            name='checksum',
        ),
        migrations.RemoveField(
            model_name='download',
            name='size',
        ),
    ]
