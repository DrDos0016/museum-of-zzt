# Generated by Django 3.2.4 on 2021-09-22 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0075_file_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='revision_details',
            field=models.TextField(blank=True, default=''),
        ),
    ]