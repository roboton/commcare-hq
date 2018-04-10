# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-07 16:11
from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0040_add_days_ration_column'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateSQLProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                 serialize=False, verbose_name='ID')),
                ('script_name', models.TextField()),
                ('query_name', models.TextField()),
                ('occurrence_time', models.DateTimeField())
            ],
        ),
    ]
