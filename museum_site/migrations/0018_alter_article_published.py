# Generated by Django 4.2.1 on 2023-06-11 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0017_alter_scroll_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='published',
            field=models.IntegerField(choices=[(1, 'Published'), (2, 'Upcoming'), (3, 'Unpublished'), (0, 'Removed'), (4, 'In Progress')], default=3, help_text='Publication Status'),
        ),
    ]