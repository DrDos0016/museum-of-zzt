# Generated by Django 3.2.4 on 2021-08-12 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0064_rename_visibile_detail_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bkzzt_topics',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='profile',
            name='closer_look_nominations',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='profile',
            name='closer_look_selections',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='profile',
            name='guest_stream_selections',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='profile',
            name='patron_tier',
            field=models.CharField(default=0, max_length=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='stream_poll_nominations',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='profile',
            name='stream_selections',
            field=models.CharField(blank=True, max_length=2000),
        ),
    ]