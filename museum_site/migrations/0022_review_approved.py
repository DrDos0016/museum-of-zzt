# Generated by Django 3.2.12 on 2022-03-08 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0021_alter_file_can_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='approved',
            field=models.BooleanField(default=True),
        ),
    ]