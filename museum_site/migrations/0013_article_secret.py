# Generated by Django 3.2.7 on 2021-12-14 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0012_auto_20211211_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='secret',
            field=models.CharField(blank=True, default='', max_length=12),
        ),
    ]