# Generated by Django 3.2.4 on 2021-06-20 23:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('museum_site', '0061_file_license'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='zeta_config',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='museum_site.zeta_config'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='zeta_config',
            name='category',
            field=models.IntegerField(choices=[(0, 'Recommended'), (1, 'Alternative'), (2, 'File Specific'), (3, 'Hidden')]),
        ),
    ]