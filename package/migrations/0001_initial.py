# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Package'
        db.create_table('package_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('all_components', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('package', ['Package'])

        # Adding M2M table for field components on 'Package'
        m2m_table_name = db.shorten_name('package_package_components')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['package.package'], null=False)),
            ('component', models.ForeignKey(orm['distribution.component'], null=False))
        ))
        db.create_unique(m2m_table_name, ['package_id', 'component_id'])


    def backwards(self, orm):
        # Deleting model 'Package'
        db.delete_table('package_package')

        # Removing M2M table for field components on 'Package'
        db.delete_table(db.shorten_name('package_package_components'))


    models = {
        'distribution.component': {
            'Meta': {'object_name': 'Component'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        },
        'package.package': {
            'Meta': {'object_name': 'Package'},
            'all_components': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['distribution.Component']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['package']