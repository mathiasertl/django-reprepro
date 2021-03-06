# Generated by Django 1.9 on 2015-12-23 17:04
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('last_seen', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('vendor', models.SmallIntegerField(choices=[(0, 'Debian'), (1, 'Ubuntu')])),
                ('last_seen', models.DateTimeField(null=True)),
                ('components', models.ManyToManyField(to='django_reprepro.Component')),
            ],
        ),
        migrations.CreateModel(
            name='IncomingDirectory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=64)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('all_components', models.BooleanField(default=False)),
                ('last_seen', models.DateTimeField(null=True)),
                ('remove_on_update', models.BooleanField(default=False, help_text='Remove package from index prior to adding a new version of the package.')),
                ('components', models.ManyToManyField(to='django_reprepro.Component')),
            ],
        ),
        migrations.CreateModel(
            name='PackageUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('version', models.CharField(max_length=32)),
                ('arch', models.CharField(max_length=8)),
                ('components', models.ManyToManyField(to='django_reprepro.Component')),
                ('dist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_reprepro.Distribution')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_reprepro.Package')),
            ],
        ),
    ]
