# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SixpackParticipant'
        db.create_table(u'djsixpack_sixpackparticipant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('experiment_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('unique_attr', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('converted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bucket', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'djsixpack', ['SixpackParticipant'])


    def backwards(self, orm):
        # Deleting model 'SixpackParticipant'
        db.delete_table(u'djsixpack_sixpackparticipant')


    models = {
        u'djsixpack.sixpackparticipant': {
            'Meta': {'object_name': 'SixpackParticipant'},
            'bucket': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'converted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'experiment_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unique_attr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['djsixpack']