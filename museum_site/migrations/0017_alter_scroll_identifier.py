# Generated by Django 3.2.17 on 2023-03-08 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0016_auto_20230228_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scroll',
            name='identifier',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]