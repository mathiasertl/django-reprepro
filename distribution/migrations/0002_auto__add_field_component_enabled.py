# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Component.enabled'
        db.add_column('distribution_component', 'enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Component.enabled'
        db.delete_column('distribution_component', 'enabled')


    models = {
        'distribution.component': {
            'Meta': {'object_name': 'Component'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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