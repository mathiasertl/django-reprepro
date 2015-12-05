# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-05 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingDirectory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=64)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
    ]
