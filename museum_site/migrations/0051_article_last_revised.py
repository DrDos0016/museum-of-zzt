# Generated by Django 3.1.7 on 2021-04-30 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0050_remove_article_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='last_revised',
            field=models.DateTimeField(blank=True, default=None, help_text='Date article content was last revised', null=True),
        ),
    ]