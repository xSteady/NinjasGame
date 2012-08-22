from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Character(models.Model):
	name=models.CharField(max_length=30)
	kind=models.IntegerField()
	base_attack=models.IntegerField()
	base_defence=models.IntegerField()
	base_treatment=models.IntegerField()
	current_health=models.IntegerField()
	level=models.IntegerField()
	exp=models.IntegerField()
	gold=models.IntegerField()
	silver=models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	
	def get_weight(self):
		return 50
	
class Item(models.Model):
	internal_name=models.CharField(max_length=100)
	type=models.IntegerField()
	perc_to_attack=models.IntegerField()
	perc_to_defence=models.IntegerField()
	perc_to_treatment=models.IntegerField()
	perc_to_exp=models.IntegerField()
	perc_to_silver=models.IntegerField()
	perc_to_health=models.IntegerField()

# Сумка, в ней слоты, предустанавливаются при создании перса
class Slot(models.Model):
	chr = models.ForeignKey(Character)
	item = models.ForeignKey(Item, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
# Что одето на персе
class Body(models.Model):
	part = models.CharField(max_length=20)
	chr = models.ForeignKey(Character)
	item = models.ForeignKey(Item, null=True)
	updated_at = models.DateTimeField(auto_now=True)

# Почтовый ящик персонажа
class Mail(models.Model):
	to_chr_id = models.IntegerField() # Сделал не через ForeignKey, т.к. не давало сделать два форенкея на одну таблицу
	from_chr_id = models.ForeignKey(Character, null=True)	# Если NULL - то от системы. 
	created_at = models.DateTimeField(auto_now_add=True)
	txt=models.CharField(max_length=2000)
