# Generated by Django 4.2.3 on 2023-09-12 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('museum_site', '0023_remove_scroll_identifier_alter_file_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback_Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('Review', 'Review'), ('Content Warning', 'Content Warning'), ('Bug Report', 'Bug Report'), ('Bug Report', 'Hints and Solutions')], max_length=25)),
            ],
        ),
        migrations.AddField(
            model_name='review',
            name='tags',
            field=models.ManyToManyField(blank=True, default=None, to='museum_site.feedback_tag'),
        ),
    ]