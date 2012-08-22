from django.db.models.fields import (SmallIntegerField, PositiveSmallIntegerField)
	
from django.conf import settings
	
class TinyIntegerField(SmallIntegerField):
	def db_type(self, connection):
		if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
			return "tinyint"
		else:
			return super(TinyIntegerField, self).db_type(connection)

class PositiveTinyIntegerField(PositiveSmallIntegerField):
	def db_type(self, connection):
		if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
			return "tinyint unsigned"
		else:
			return super(PositiveTinyIntegerField, self).db_type(connection)