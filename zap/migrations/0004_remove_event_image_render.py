# Generated by Django 3.2.17 on 2023-03-03 01:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zap', '0003_auto_20230303_0038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='image_render',
        ),
    ]