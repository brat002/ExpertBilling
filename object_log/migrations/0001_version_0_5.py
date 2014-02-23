# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'LogAction'
        db.create_table('object_log_logaction', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, primary_key=True)),
            ('template', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('object_log', ['LogAction'])

        # Adding model 'LogItem'
        db.create_table('object_log_logitem', (
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('object_id3', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('object_id2', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('object_id1', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_items', to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['object_log.LogAction'])),
            ('object_type1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_items1', null=True, to=orm['contenttypes.ContentType'])),
            ('object_type2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_items2', null=True, to=orm['contenttypes.ContentType'])),
            ('object_type3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_items3', null=True, to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('object_log', ['LogItem'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'LogAction'
        db.delete_table('object_log_logaction')

        # Deleting model 'LogItem'
        db.delete_table('object_log_logitem')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'object_log.logaction': {
            'Meta': {'object_name': 'LogAction'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'object_log.logitem': {
            'Meta': {'object_name': 'LogItem'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['object_log.LogAction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id1': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'object_id2': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'object_id3': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'object_type1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_items1'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'object_type2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_items2'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'object_type3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_items3'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_items'", 'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['object_log']
