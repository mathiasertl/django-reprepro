# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Package.remove_on_update'
        db.add_column('package_package', 'remove_on_update',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Package.remove_on_update'
        db.delete_column('package_package', 'remove_on_update')


    models = {
        'distribution.component': {
            'Meta': {'object_name': 'Component'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        },
        'package.package': {
            'Meta': {'object_name': 'Package'},
            'all_components': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['distribution.Component']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'remove_on_update': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['package']