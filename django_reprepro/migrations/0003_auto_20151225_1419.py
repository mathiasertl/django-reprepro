# Generated by Django 1.9 on 2015-12-25 13:19
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_reprepro', '0002_auto_20151225_1348'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PackageUpload',
            new_name='SourcePackage',
        ),
    ]
