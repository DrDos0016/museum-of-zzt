# Generated by Django 3.2.7 on 2021-12-01 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0009_auto_20211201_1851'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='preview',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
    ]