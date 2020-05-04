# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-27 16:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0046_new_plans'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerInvoiceCommunicationHistory',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('date_created', models.DateField(auto_now_add=True)),
                ('communication_type', models.CharField(
                    choices=[
                        ('OTHER', 'other'),
                        ('OVERDUE_INVOICE', 'Overdue Invoice'),
                        ('DOWNGRADE_WARNING', 'Subscription Pause Warning'),
                    ],
                    default='OTHER',
                    max_length=25
                )),
                ('invoice', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='accounting.CustomerInvoice',
                )),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceCommunicationHistory',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('date_created', models.DateField(auto_now_add=True)),
                ('communication_type', models.CharField(
                    choices=[
                        ('OTHER', 'other'),
                        ('OVERDUE_INVOICE', 'Overdue Invoice'),
                        ('DOWNGRADE_WARNING', 'Subscription Pause Warning'),
                    ],
                    default='OTHER', max_length=25)),
                ('invoice', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='accounting.Invoice',
                )),
            ],
            options={
                'abstract': False,
            },
        ),
    ]