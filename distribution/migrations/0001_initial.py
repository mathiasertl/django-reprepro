# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Component'
        db.create_table('distribution_component', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal('distribution', ['Component'])

        # Adding model 'Distribution'
        db.create_table('distribution_distribution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('vendor', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('distribution', ['Distribution'])

        # Adding M2M table for field components on 'Distribution'
        m2m_table_name = db.shorten_name('distribution_distribution_components')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('distribution', models.ForeignKey(orm['distribution.distribution'], null=False)),
            ('component', models.ForeignKey(orm['distribution.component'], null=False))
        ))
        db.create_unique(m2m_table_name, ['distribution_id', 'component_id'])


    def backwards(self, orm):
        # Deleting model 'Component'
        db.delete_table('distribution_component')

        # Deleting model 'Distribution'
        db.delete_table('distribution_distribution')

        # Removing M2M table for field components on 'Distribution'
        db.delete_table(db.shorten_name('distribution_distribution_components'))


    models = {
        'distribution.component': {
            'Meta': {'object_name': 'Component'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        },
        'distribution.distribution': {
            'Meta': {'object_name': 'Distribution'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['distribution.Component']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'vendor': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['distribution']