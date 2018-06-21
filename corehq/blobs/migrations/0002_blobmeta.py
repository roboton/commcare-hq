# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 19:08
from __future__ import unicode_literals

import datetime
import jsonfield.fields
import partial_index
from django.db import migrations, models

import corehq.blobs.models
from corehq.sql_db.operations import RawSQLMigration


migrator = RawSQLMigration(('corehq', 'blobs', 'sql_templates'), {})


class Migration(migrations.Migration):

    dependencies = [
        ('blobs', '0001_squashed_0009_domains'),
    ]

    operations = [
        migrations.CreateModel( # TODO rewrite as rename of xformattachmentsql
                                # will need to reverse this migration on local/test dbs
            name='BlobMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=255)),
                ('parent_id', models.CharField(db_index=True, max_length=255)),
                ('name', models.CharField(default=None, max_length=255, null=True)),
                ('path', models.CharField(default=corehq.blobs.models.uuid4_hex, max_length=255, unique=True)),
                ('type_code', models.PositiveSmallIntegerField()),
                ('content_length', models.PositiveIntegerField()),
                ('content_type', models.CharField(max_length=255, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('expires_on', models.DateTimeField(default=None, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='blobmeta',
            index=partial_index.PartialIndex(fields=['expires_on'], name='blobs_blobm_expires_64b92d_partial', unique=False, where='expires_on IS NOT NULL', where_postgresql=b'', where_sqlite=b''),
        ),
        migrator.get_migration('delete_blob_meta.sql'),
    ]
