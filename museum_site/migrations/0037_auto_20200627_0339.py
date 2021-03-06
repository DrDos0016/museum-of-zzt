# Generated by Django 3.0.7 on 2020-06-27 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0036_wozzt_queue'),
    ]

    operations = [
        migrations.AddField(
            model_name='wozzt_queue',
            name='board_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='wozzt_queue',
            name='dark',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wozzt_queue',
            name='shot_limit',
            field=models.IntegerField(default=255),
        ),
        migrations.AddField(
            model_name='wozzt_queue',
            name='time_limit',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='wozzt_queue',
            name='uuid',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wozzt_queue',
            name='zap',
            field=models.BooleanField(default=False),
        ),
    ]
