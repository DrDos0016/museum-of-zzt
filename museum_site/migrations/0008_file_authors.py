# Generated by Django 3.2.15 on 2022-10-12 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0007_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='authors',
            field=models.ManyToManyField(blank=True, default=None, to='museum_site.Author'),
        ),
    ]