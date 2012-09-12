from django.db import models
from django.contrib.auth.models import User

# Всякие параметры
import settings
from settings import BuildingTypes, SlotTypes, FigthStatuses, MissionTypes
from tinyint import PositiveTinyIntegerField

import datetime
from datetime import timedelta
from django.utils.timezone import utc

import time

import random
import ast

# https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name="profile", primary_key=True)
	
	renewal=models.PositiveSmallIntegerField()	# Скорость восстановления энергии
	village_name=models.CharField(max_length=100)
	village_level=models.PositiveSmallIntegerField(default=0)
	
	store_level=PositiveTinyIntegerField(default=0)		# Уровень склада, по нему определяется, сколько ресурсов может храниться
	
	gold = models.PositiveIntegerField(default=0)
	silver = models.PositiveIntegerField(default=0)
	
	rice=models.PositiveSmallIntegerField(default=0)	# Количество риса на складе
	wood=models.PositiveSmallIntegerField(default=0)	# Дерево
	stone=models.PositiveSmallIntegerField(default=0)	# Камень
	coal=models.PositiveSmallIntegerField(default=0)	# Уголь
	metal=models.PositiveSmallIntegerField(default=0)	# Метал
	crystal=models.PositiveIntegerField(default=0)		# Кристалы
	poison=models.PositiveIntegerField(default=0)		# яды
	
	village_distribution=models.CharField(max_length=100) # Выбранное для этой деревни распределение ресурсов в деревне
	mine_distribution=models.CharField(max_length=100) # Выбранное для этой деревни распределение ресурсов в шахте
	
	# Добавление ресурса на склад. product - что добавляется, count - сколько добавлять
	def add_to_store(self, building):
		old_cnt = None  # Сколько есть сейчас на складе
		cnt = {}		# Cколько стало на складе после добавления
		max = STORE_MAXIMUMS[self.store_level]		# Какой максимум склада
		lost = {}		# Сколько потеряно из-за переполнения склада
		produced = {} 	# Сколько произведено каждого товара
		
		if (building.type_id == BuildingTypes.FIELD):
			old_cnt = {"r":self.rice, "w": self.wood}
			distribution = ast.literal_eval(self.village_distribution)
		elif (building.type_id == BuildingTypes.MINE):
			old_cnt = {"s":self.stone, "c":self.coal, "m":self.metal, "cr":self.crystal}
			distribution = ast.literal_eval(self.mine_distribution)
		else:
			return None
		
		# Просто инициализация словарей таким же словарем как и old_cnt, ниже в цикле наполняются значениями
		#cnt = old_cnt
		#lost = old_cnt
		
		increase = building.recount()
		
		# Здание ничего не произвело
		if (increase == None):
			return None

		# Переменная для отладки
		str_keys = "Produced: " + str(increase) + "<br />"
		
		# Прохождение по всем ключам текущих значений
		for k in old_cnt:
			# Сколько данного ресурса добылось, согласно распределению
			value = increase * distribution[k] / distribution["base"]
			# Сколько этого ресурса должно оказаться на складе
			new_value = old_cnt[k] + value
			# Сколько не влезло на склад
			lost_cnt = new_value - max[k]
			
			if (lost_cnt > 0):
				new_value = max[k]
			else:
				lost_cnt = 0
			
			str_keys += k + ": " + str(distribution[k]) + " # Got: " + str(value) + " # Old Value: " + str(old_cnt[k]) + " # New Value: " + str(new_value) + " # Limit: " + str(max[k]) + " # Lost: " + str(lost_cnt) + "<br />"
			
			cnt[k] = new_value	# Сколько стало этого товара на складе
			lost[k] = lost_cnt	# Сколько утрачено из-за переполнения склада
			produced[k] = value	# Сколько произведено этого товара
			
		#return str_keys
		#return str(old_cnt) + "<br />" + str(cnt) + "<br />" + str(lost)

		# Простановка необходимых значений
		if (building.type_id == BuildingTypes.FIELD):
			self.rice = cnt['r']
			self.wood = cnt['w']
		elif (building.type_id == BuildingTypes.MINE):
			self.stone = cnt['s']
			self.coal = cnt['c']
			self.metal = cnt['m']
			self.crystal = cnt['cr']
		
		# old_store - товаров на складе до расчета прибавки
		# new_store - товаров на складе после расчета прибавки
		# increase - всего добыто ресурсов
		# lost - потеряно ресурсов из-за переполнения склада
		# produced - произведено каждого ресурса
		return {'old_store': old_cnt, 'new_store': cnt, 'increase': increase, 'lost': lost, 'produced': produced }
			
# Create your models here.
class Character(models.Model):
	name=models.CharField(max_length=30)
	strength=models.PositiveSmallIntegerField(default=0)			# Сила
	adroitness=models.PositiveSmallIntegerField(default=0)			# Ловкость
	endurance=models.PositiveSmallIntegerField(default=0)			# Выносливость
	luck=models.PositiveSmallIntegerField(default=0)				# Удача
	will=models.PositiveSmallIntegerField(default=0)				# Воля
	honour=models.PositiveSmallIntegerField(default=0)				# Честь
	
	health=PositiveTinyIntegerField(default=0)						# Здоровье
	energy=models.PositiveSmallIntegerField(default=0)				# Энергия
	
	is_bot=models.BooleanField(default=0)							# Если бот, то true
	mission_id=models.IntegerField(blank=True, null=True)			# ID миссии на которой сейчас находиться
	mission_type_id=models.PositiveSmallIntegerField(blank=True, null=True)			# ID типа миссии на которой сейчас находиться
	mission_finish_dt=models.DateTimeField(blank=True, null=True)	# Когда вернется с миссии
	
	exp=models.PositiveIntegerField(default=0)
	level=PositiveTinyIntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	fraction=models.PositiveSmallIntegerField()						# Дублирую из UserProfile, что б не селектить
	
	def get_weight(self):
		# Определение увеличения силы атаки и силы обороны
		#from django.db import connection
		#cursor = connection.cursor()
		#cursor.execute("SELECT COALESCE(SUM(perc_to_attack), 0), COALESCE(SUM(perc_to_defence), 0) FROM main_slot s INNER JOIN main_item i ON s.`item_id` = i.`id` WHERE s.`chr_id` = %s" , [str(self.id)])
		#res = cursor.fetchone()
		
		#weight = float((self.exp + self.attack*(100 + res[0])/100 + self.defence*(100 + res[1])/100)*self.health/100)
		#return weight
		return float(self.strength * self.adroitness + self.endurance)
	
	# Определение максимальных значений, до которых можно прокачать параметры во время тренировки. В зависимости от типа и уровня
	def get_max_training_values_inc(self):
		return MAX_TRAINING_VALUES[self.fraction][self.level]
		
	# Определение значений прироста силы атаки, защиты и способности к лечению, после победы, в зависимости от уровня и рассы
	def get_values_inc(self):
		return VALUES_INCS[self.fraction][self.level]
		
	def get_honour_sub(self):
		return HONOUR_SUB[self.fraction][self.level]

	def get_honour_inc(self):
		return HONOUR_INC[self.fraction][self.level]
		
	# Добавление экспы за победу и переход на следующий уровень, если надо
	def add_exp_and_silver_for_win(self):
		self.exp += self.get_exp_inc_for_win();
		# Если экспа достигла и/или превысила порог для перехода на следующий уровень и максимальный уровень еще не достигнут, то переходим на следующий уровень
		if (self.exp >= self.get_exp_threshold() and self.level < self.get_max_level()):
			self.level += 1
			
		self.silver += self.get_silver_inc_for_win()
			
	# Получение порогов экспы для переходов на новые уровни
	def get_exp_threshold(self):
		# Уровен с КОТОРОГО переходят, является индексом массива
		return EXP_TO_LEVELUP[self.level]
	
	# Получение прироста экспы за победу в бою, в зависимости от уровня
	def get_exp_inc_for_win(self):
		return EXP_FOR_WIN[self.level]
	
	# Получение прироста серебра за победу в бою, в зависимости от уровня
	def get_silver_inc_for_win(self):
		return SILVER_FOR_WIN[self.level]
		
	# Получение максимального возможного уровня
	def get_max_level(self):
		return MAX_LEVEL
		
	#def is_on_mission(self, mission_type_id):
	#	return False
		
	@property
	def is_on_mission(self):
		if (self.mission_id != None): #  and (self.mission_finish_dt != None or self.mission_finish_dt > datetime.datetime.now())
			if (self.mission_finish_dt == None):
				return 2 # персонаж на миссии и ее можно отменить (т.к. безссрочная, например Охрана деревни)
			#elif (self.mission_finish_dt.replace(tzinfo=None) > datetime.datetime.now().replace(tzinfo=None)):
			elif (self.mission_finish_dt > datetime.datetime.now()):
				return 1 # персонаж на миссии, у которой есть время окончания и ее нельзя отменить
			else:
				return 0 # У персонажа есть запись о прошедшей миссии
				
		return 0 # У игрока нет записи о миссии
	
	@property
	def mission_name(self):
		if (self.mission_type_id != None and self.mission_type_id >= 0 and self.mission_type_id < len(MISSION_NAMES)):
			return MISSION_NAMES[self.mission_type_id]
		
		return ''
		
	@property
	def mission_time(self):
		#now = datetime.datetime.now().replace(tzinfo=None)
		now = datetime.datetime.now()
		#dt = self.mission_finish_dt.replace(tzinfo=None)
		dt = self.mission_finish_dt
		if (self.mission_finish_dt != None and dt > now):
			dd = (dt - now)
			sec = dd.days*86400 + dd.seconds

			#return PHRASES[8].replace('#sec#', str(sec))
			if (sec < 120):
				return PHRASES[8].replace('#sec#', str(sec))
			else:
				return PHRASES[7].replace('#min#', str(sec/60))
		
		return ''
	
	@staticmethod
	def create_new_char(user):
		default_chr = BASE_CHARACTER
		new_chr = Character(name=default_chr['name'], strength=default_chr['strength'], adroitness=default_chr['adroitness'], endurance=default_chr['endurance'], luck=default_chr['luck'], will=default_chr['will'], honour=default_chr['honour'], health=default_chr['health'], energy=default_chr['energy'], exp=default_chr['exp'], level=default_chr['level'], user=user, fraction=0)
		
		# TODO Обработка ошибки
		new_chr.save()
		
		# Создание слотов для оружия на персонаже
		slot1 = Slot(chr=new_chr, type_id = SlotTypes.MAIN)
		slot2 = Slot(chr=new_chr, type_id = SlotTypes.THROWING)
		slot3 = Slot(chr=new_chr, type_id = SlotTypes.CHEMISTRY)
		
		# TODO Обработка ошибки
		slot1.save()
		slot2.save()
		slot3.save()
		
		return new_chr
	
# Здания в деревне
class Building(models.Model):
	user = models.ForeignKey(User)
	type_id = PositiveTinyIntegerField(default=0)			# Тип здания 0-поле, 1-шахта, 2-библиотека
	level = PositiveTinyIntegerField(default=0)				# Уровень здания
	cnt = models.PositiveSmallIntegerField(default=0)		# Количественный показатель, для каждого типа здания значит что то свое
	last_check_out = models.DateTimeField(auto_now_add=True)					# Дата последнего пересчета количества ресурсов
	
	# С 2012-08-22 просто возвращает сколько сгенерило здание с момента последнего посещения 
	# Устанавливает себе последнее время проверки генерации ресурсов
	def recount(self):
		speed = BUILDING_PRODUCE_SPEED[self.type_id][self.level]
		
		#now = datetime.datetime.utcnow()
		now = datetime.datetime.now()
		#dt = self.last_check_out.replace(tzinfo=None)
		dt = self.last_check_out
		
		# Получение разницы в часах (получается без дробной части, т.к. date_diff возвращает INT)
		hours =  Helper.date_diff(dt, now)/ 3600
		
		#hours = 2
		# Количество полных циклов производства
		production_steps = hours / speed[1]
		
		if (production_steps == 0):
			return None
		
		produced = speed[0] * production_steps
		
		# Время последнего чекаута, учитывая, что шаг (production_step) может быть больше часа (но кратный часу) и целочисленное количество совершенных шагов может не попадать на текущее время
		self.last_check_out = dt + timedelta(seconds=production_steps*speed[1]*3600)
		
		#return "hours=" + str(hours) + "<br />production_steps=" + str(production_steps) + "<br />production_steps * step=" + str(production_steps*speed[1]) + "<br/>last_check_out="  + str(dt) + "<br />new_check_out=" + str(dt + timedelta(seconds=production_steps*speed[1]*3600)) + "<br />now=" + str(now)
		#return str(produced) + " " + str(speed[0]) + " " + str(hours) + " " + str(speed[1]) + " " + str(production_steps)
		
		# Возвращаем количество произведенных ресурсов
		return produced

class Fight(models.Model):
	created_at = models.DateTimeField(auto_now_add=True) 			# Дата создания боя
	finished_at = models.DateTimeField(blank=True,null=True)		# Дата завершения боя
	status = models.SmallIntegerField(default=0)					# Статус боя: 0 - не закончен, 1-Произошел бой, 2-Атакующий отменил бой, 3-закрыт по таймауту
																	# settings.py FigthStatuses
	type = models.SmallIntegerField(default=0)						# Тип боя - вызов, караван, и т.д. settings.py MissionTypes
	res = models.FloatField(blank=True,null=True)					# Результат боя
	enable_dismiss = models.BooleanField()							# Было ли разрешено отменить бой
	
	a_user_id=models.IntegerField()									# ID пользователя, который нападает
	a_chr_id=models.IntegerField()									# ID персонажа, который нападает
	a_mission_id = models.IntegerField(blank=True,null=True)		# ID миссии нападающего, если бой в рамках миссии
	
	# ПАРАМЕТРЫ НАПАДАЮЩЕГО ПЕРЕД БОЕМ
	a_b_strength=models.PositiveSmallIntegerField(default=0)		# Сила
	a_b_adroitness=models.PositiveSmallIntegerField(default=0)		# Ловкость
	a_b_endurance=models.PositiveSmallIntegerField(default=0)		# Выносливость
	a_b_luck=models.PositiveSmallIntegerField(default=0)			# Удача
	a_b_will=models.PositiveSmallIntegerField(default=0)			# Воля
	a_b_honour=models.PositiveSmallIntegerField(default=0)			# Честь
	a_b_health=PositiveTinyIntegerField(default=0)					# Здоровье
	a_b_energy=models.PositiveSmallIntegerField(default=0)			# Энергия
	a_b_exp=models.PositiveIntegerField(default=0)					# Экспа
	a_b_level=PositiveTinyIntegerField(default=0)					# Левел
	
	# ПАРАМЕТРЫ НАПАДАЮЩЕГО ПОСЛЕ БОЯ
	a_e_strength=models.PositiveSmallIntegerField(default=0)		# Сила
	a_e_adroitness=models.PositiveSmallIntegerField(default=0)		# Ловкость
	a_e_endurance=models.PositiveSmallIntegerField(default=0)		# Выносливость
	a_e_luck=models.PositiveSmallIntegerField(default=0)			# Удача
	a_e_will=models.PositiveSmallIntegerField(default=0)			# Воля
	a_e_honour=models.PositiveSmallIntegerField(default=0)			# Честь
	a_e_health=PositiveTinyIntegerField(default=0)					# Здоровье
	a_e_energy=models.PositiveSmallIntegerField(default=0)			# Энергия
	a_e_exp=models.PositiveIntegerField(default=0)					# Экспа
	a_e_level=PositiveTinyIntegerField(default=0)					# Левел
	
	# Инфа о том, на кого нападают
	d_user_id=models.IntegerField()									# ID пользователя, на которого нападают
	d_chr_id=models.IntegerField()									# ID персонажа, на которого нападают
	d_mission_id = models.IntegerField(blank=True,null=True)		# ID миссии защищающегося, если бой в рамках миссии защищающегося
	
	# ПАРАМЕТРЫ ПЕРЕД БОЕМ НА КОГО НАПАДАЮТ
	d_b_strength=models.PositiveSmallIntegerField(default=0)		# Сила
	d_b_adroitness=models.PositiveSmallIntegerField(default=0)		# Ловкость
	d_b_endurance=models.PositiveSmallIntegerField(default=0)		# Выносливость
	d_b_luck=models.PositiveSmallIntegerField(default=0)			# Удача
	d_b_will=models.PositiveSmallIntegerField(default=0)			# Воля
	d_b_honour=models.PositiveSmallIntegerField(default=0)			# Честь
	d_b_health=PositiveTinyIntegerField(default=0)					# Здоровье
	d_b_energy=models.PositiveSmallIntegerField(default=0)			# Энергия
	d_b_exp=models.PositiveIntegerField(default=0)					# Экспа
	d_b_level=PositiveTinyIntegerField(default=0)					# Левел
	
	# ПАРАМЕТРЫ ПЕРЕД БОЕМ НА КОГО НАПАДАЮТ
	d_e_strength=models.PositiveSmallIntegerField(default=0)		# Сила
	d_e_adroitness=models.PositiveSmallIntegerField(default=0)		# Ловкость
	d_e_endurance=models.PositiveSmallIntegerField(default=0)		# Выносливость
	d_e_luck=models.PositiveSmallIntegerField(default=0)			# Удача
	d_e_will=models.PositiveSmallIntegerField(default=0)			# Воля
	d_e_honour=models.PositiveSmallIntegerField(default=0)			# Честь
	d_e_health=PositiveTinyIntegerField(default=0)					# Здоровье
	d_e_energy=models.PositiveSmallIntegerField(default=0)			# Энергия
	d_e_exp=models.PositiveIntegerField(default=0)					# Экспа
	d_e_level=PositiveTinyIntegerField(default=0)					# Левел
			
	
	# Разница силы до и после боя у АТАКУЮЩЕГО
	@property
	def diff_strength_a(self):
		return self.a_e_strength - self.a_b_strength
		
	# Разница ловкости до и после боя у АТАКУЮЩЕГО
	@property
	def diff_adroitness_a(self):
		return self.a_e_adroitness - self.a_b_adroitness
		
	# Разница выносливости до и после боя у АТАКУЮЩЕГО
	@property
	def diff_endurance_a(self):
		return self.a_e_endurance - self.a_b_endurance
		
	# Разница удача до и после боя у АТАКУЮЩЕГО
	@property
	def diff_luck_a(self):
		return self.a_e_luck - self.a_b_luck
		
	# Разница воля до и после боя у АТАКУЮЩЕГО
	@property
	def diff_will_a(self):
		return self.a_e_will - self.a_b_will

	# Разница чести до и после боя у АТАКУЮЩЕГО
	@property
	def diff_honour_a(self):
		return self.a_e_honour - self.a_b_honour
		
	# Разница здоровья до и после боя у АТАКУЮЩЕГО
	@property
	def diff_health_a(self):
		return self.a_e_health - self.a_b_health
		
	# Разница энергии до и после боя у АТАКУЮЩЕГО
	@property
	def diff_energy_a(self):
		return self.a_e_energy - self.a_b_energy	
		
	# Разница экспы до и после боя у АТАКУЮЩЕГО
	@property
	def diff_exp_a(self):
		return self.a_e_exp - self.a_b_exp

	# Разница силы до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_strength_d(self):
		return self.d_e_strength - self.d_b_strength
		
	# Разница ловкости до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_adroitness_d(self):
		return self.d_e_adroitness - self.d_b_adroitness
		
	# Разница выносливости до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_endurance_d(self):
		return self.d_e_endurance - self.d_b_endurance
		
	# Разница удача до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_luck_d(self):
		return self.d_e_luck - self.d_b_luck
		
	# Разница воля до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_will_d(self):
		return self.d_e_will - self.d_b_will

	# Разница чести до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_honour_d(self):
		return self.d_e_honour - self.d_b_honour
		
	# Разница здоровья до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_health_d(self):
		return self.d_e_health - self.d_b_health
		
	# Разница энергии до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_energy_d(self):
		return self.d_e_energy - self.d_b_energy	
		
	# Разница экспы до и после боя у ЗАЩИЩАЮЩЕГОСЯ
	@property
	def diff_exp_d(self):
		return self.d_e_exp - self.d_b_exp

	# Отмена боя, проверка возможности отмены и получение из базы атакующего (a) и обороняющегося (d) происходит в вызывающем методе
	def dissmiss(self, a, d):
		a.honour = a.honour - a.get_honour_sub()
		d.honour = d.honour + d.get_honour_inc()
	
		self.set_new_values(a, d)
	
		self.status = FigthStatuses.DISMISSED
	
	def attack(self, a, d):
		# Вес атакующего
		chr_a_weight = a.get_weight()
		# Вес защищающегося
		chr_d_weight = d.get_weight()
		# Вероятность победы атакующего
		win_pr = float(chr_a_weight) / (chr_a_weight + chr_d_weight)
		
		# Результат. Если  > 0 - то победа, < 0 - поражение. Значение по модулю - коэффициент урона проигравшему
		# Если res > 0, то чем больше, тем уверенее победа
		# Если res < 0, то чем больше по модулю, тем сильнее поражение
		res = win_pr - random.random()
		
		if (res < 0 and abs(res) < 0.01):
			res = -0.01
		elif (res >= 0 and res < 0.01):
			res = 0.01
			
		winner = a
		loser = d

		# Победил атакующий
		if (res < 0):
			winner = d
			loser = a
			#result_response = -1
			#result_name = WORDS[7]
			#result_status = 'loss'

		# Модуль результата
		abs_res = abs(res)
		
		# Получение массивов изменения значений
		winner_values_inc = winner.get_values_inc()
		loser_values_inc = loser.get_values_inc()
		
		# Маска, какие параметры с каким коэфициентом увеличиваются у победителя
		winner_mask = [10, 10, 10, 10, 10, 0, 0, 1] # strength, adroitness, endurance, luck, will, honour, health, exp
		# Маска, какие параметры с каким коэфициентом уменьшаются у проигравшего
		loser_mask = [0, 0, 0, 0, 0, 0, 10, 0] # strength, adroitness, endurance, luck, will, honour, health, exp
		
		# Можно вернуть лог изменений
		trace = 'RES: ' + str(res) + '<br />'
		
		trace += 'WINNER:<br />strength: ' + str(winner.strength) 
		winner.strength = winner.strength + int(winner_values_inc[0] * winner_mask[0] * abs_res)
		trace += ' -> ' + str(winner.strength) + '<br />adroitness: ' + str(winner.adroitness)
		winner.adroitness = winner.adroitness + int(winner_values_inc[1] * winner_mask[1] * abs_res)
		trace += ' -> ' + str(winner.adroitness) + '<br />endurance: ' + str(winner.endurance)
		winner.endurance = winner.endurance + int(winner_values_inc[2] * winner_mask[2] * abs_res)
		trace += ' -> ' + str(winner.endurance) + '<br />luck: ' + str(winner.luck)
		winner.luck = winner.luck + int(winner_values_inc[3] * winner_mask[3] * abs_res)
		trace += ' -> ' + str(winner.luck) + '<br />will: ' + str(winner.will)
		winner.will = winner.will + int(winner_values_inc[4] * winner_mask[4] * abs_res)
		trace += ' -> ' + str(winner.will) + '<br />honour: ' + str(winner.honour)
		winner.honour = winner.honour + int(winner_values_inc[5] * winner_mask[5] * abs_res)
		trace += ' -> ' + str(winner.honour) + '<br />health: ' + str(winner.health)
		winner.health = winner.health + int(winner_values_inc[6] * winner_mask[6] * abs_res)
		trace += ' -> ' + str(winner.health) + '<br />exp: ' + str(winner.exp)
		winner.exp = winner.exp + int(winner_values_inc[7] * winner_mask[7])
		trace += ' -> ' + str(winner.exp) + '<br /><br />'
		
		trace += 'LOSER:<br />strength: ' + str(loser.strength) 
		loser.strength = loser.strength - int(loser_values_inc[0] * loser_mask[0] * abs_res)
		trace += ' -> ' + str(loser.strength) + '<br />adroitness: ' + str(loser.adroitness)
		loser.adroitness = loser.adroitness - int(loser_values_inc[1] * loser_mask[1] * abs_res)
		trace += ' -> ' + str(loser.adroitness) + '<br />endurance: ' + str(loser.endurance)
		loser.endurance = loser.endurance - int(loser_values_inc[2] * loser_mask[2] * abs_res)
		trace += ' -> ' + str(loser.endurance) + '<br />luck: ' + str(loser.luck)
		loser.luck = loser.luck - int(loser_values_inc[3] * loser_mask[3] * abs_res)
		trace += ' -> ' + str(loser.luck) + '<br />will: ' + str(loser.will)
		loser.will = loser.will - int(loser_values_inc[4] * loser_mask[4] * abs_res)
		trace += ' -> ' + str(loser.will) + '<br />honour: ' + str(loser.honour)
		loser.honour = loser.honour - int(loser_values_inc[5] * loser_mask[5] * abs_res)
		trace += ' -> ' + str(loser.honour) + '<br />health: ' + str(loser.health)
		trace += '<br/><br/>loser_values_inc[6]: ' + str(loser_values_inc[6]) + '     loser_mask[6]: ' + str(loser_mask[6]) + '<br/>' + str(loser_values_inc[6] * loser_mask[6] * abs_res) + '<br><br>'
		loser.health = loser.health - int(loser_values_inc[6] * loser_mask[6] * abs_res)
		trace += ' -> ' + str(loser.health) + '<br />exp: ' + str(loser.exp)
		loser.exp = loser.exp - int(loser_values_inc[7] * loser_mask[7])
		trace += ' -> ' + str(loser.exp) + '<br /><br />'
		
		# Исключение отрицательных значений
		loser.strength = loser.strength if loser.strength >= 0  else 0
		loser.adroitness = loser.adroitness if loser.adroitness >= 0  else 0
		loser.endurance = loser.endurance if loser.endurance >= 0  else 0
		loser.luck = loser.luck if loser.luck >= 0  else 0
		loser.will = loser.will if loser.will >= 0  else 0
		loser.honour = loser.honour if loser.honour >= 0  else 0
		loser.health = loser.health if loser.health >= 0  else 0
		loser.exp = loser.exp if loser.exp >= 0  else 0
		
		# Установка значений после боя
		self.set_new_values(a, d)
		
		self.status = FigthStatuses.FINISHED
		
		return res
		
	# Установка значений перед боем (надо вызывать сразу после конструктора
	def set_start_values(self, a, d):
		self.a_b_strength=a.strength
		self.a_b_adroitness=a.adroitness
		self.a_b_endurance=a.endurance
		self.a_b_luck=a.luck
		self.a_b_will=a.will
		self.a_b_honour=a.honour
		self.a_b_health=a.health
		self.a_b_energy=a.energy
		self.a_b_exp=a.exp
		self.a_b_level=a.level

		self.d_b_strength=d.strength
		self.d_b_adroitness=d.adroitness
		self.d_b_endurance=d.endurance
		self.d_b_luck=d.luck
		self.d_b_will=d.will
		self.d_b_honour=d.honour
		self.d_b_health=d.health
		self.d_b_energy=d.energy
		self.d_b_exp=d.exp
		self.d_b_level=d.level
			
	# Установка значений атакующего (a) и защищающегося (d) после боя
	def set_new_values(self, a, d):
		self.a_e_strength=a.strength				# Сила
		self.a_e_adroitness=a.adroitness			# Ловкость
		self.a_e_endurance=a.endurance				# Выносливость
		self.a_e_luck=a.luck						# Удача
		self.a_e_will=a.will						# Воля
		self.a_e_honour=a.honour					# Честь
		self.a_e_health=a.health					# Здоровье
		self.a_e_energy=a.energy					# Энергия
		self.a_e_exp=a.exp							# Экспа
		self.a_e_level=a.level						# Уровень
		
		self.d_e_strength=d.strength				# Сила
		self.d_e_adroitness=d.adroitness			# Ловкость
		self.d_e_endurance=d.endurance				# Выносливость
		self.d_e_luck=d.luck						# Удача
		self.d_e_will=d.will						# Воля
		self.d_e_honour=d.honour					# Честь
		self.d_e_health=d.health					# Здоровье
		self.d_e_energy=d.energy					# Энергия
		self.d_e_exp=d.exp							# Экспа
		self.d_e_level=d.level						# Уровень

class Mission(models.Model):
	user_id=models.IntegerField()									# ID пользователя
	chr_id=models.IntegerField()									# ID персонажа
	level=PositiveTinyIntegerField(default=0)						# Левел персонажа на момент начала миссии
	
	type = models.SmallIntegerField(default=0)						# Тип миссии - вызов, караван, и т.д. settings.py MissionTypes
	
	created_at = models.DateTimeField(auto_now_add=True) 			# Дата создания миссии
	finished_at = models.DateTimeField(blank=True,null=True)		# Дата завершения боя. Если не NULL и < curreent_date, то миссия завершена
	
	fight_id = models.IntegerField(blank=True,null=True)			# ID последенего боя
	fight_res = models.FloatField(blank=True,null=True)				# Результат последнего боя (Прям как в логе боев записано - т.е. если перс охраняет деревню, то он защищающийся в бое будет и для него по-идее надо инвертировать результат, т.к. если нападавший выиграл, то он проиграл, но здесь как есть в бою!!)
	fight_dt = models.DateTimeField(blank=True,null=True)			# Дата окончания последнего боя
	
	# Сохраняет новую миссию и обновляет чара
	def save_new(self, chr):
		# TODO Транзакция
		self.save()
		
		chr.mission_id = self.id
		chr.mission_type_id = self.type
		chr.mission_finish_dt = self.finished_at
		# TODO Транзакция
		chr.save()
	
	# Возвращение чара с миссии - закрывает миссию, накидывает нужные блага и сохраняет чара
	def cancel(self, chr):
		now = datetime.datetime.now() #.utcnow().replace(tzinfo=utc)
		
		self.finished_at = now
		chr.mission_finish_dt = now
		
		arr = None
		
		if (self.type == MissionTypes.MEDITATION):
			#mins = (now - self.created_at.replace(tzinfo=utc)).seconds / 60
			mins = (now - self.created_at).seconds / 60
			new_luck = chr.luck + mins*LUCK_INCREASE[chr.level][0]
			
			# Ограничение максимума удачи
			if (new_luck > LUCK_INCREASE[chr.level][1]):
				new_luck = LUCK_INCREASE[chr.level][1]
			
			# Т.к. есть ограничение, то реальный прирост может быть нулевым
			luck_change = new_luck - chr.luck
			
			arr = {"mins": mins, "luck_change": luck_change, "old_luck": chr.luck, "new_luck": new_luck}
			
			chr.luck = new_luck
		
		# TODO Транзакция
		self.save()
		chr.save()
		
		return arr
		
class Item(models.Model):
	internal_name=models.CharField(max_length=100)
	type_id=PositiveTinyIntegerField()						# Тип оружия settings.py SlotTypes
	damage=models.PositiveSmallIntegerField()				# Дамаг

# Слоты на персе
class Slot(models.Model):
	chr = models.ForeignKey(Character)
	type_id = PositiveTinyIntegerField(default=0)			# Тип оружия settings.py SlotTypes
	item = models.ForeignKey(Item, null=True)
	updated_at = models.DateTimeField(auto_now=True)		
	
# Склад
class Store(models.Model):
	user = models.ForeignKey(User)
	item = models.ForeignKey(Item)
	created_at = models.DateTimeField(auto_now_add=True) 	
	from_workshop = models.BooleanField()					# True - если вещь пришла на скалд из мастерской
	
class BattleLog(models.Model):
	created_at = models.DateTimeField(auto_now_add=True) 	# Дата создания боя
	finished_at = models.DateTimeField(blank=True,null=True)			# Дата завершения боя
	status = models.SmallIntegerField(default=0)			# Статус боя: 0 - не закончен, 1-Произошел бой, 2-Атакующий отменил бой, 3-закрыт по таймауту
	res = models.FloatField(blank=True,null=True)			# Результат боя
	enable_dismiss = models.BooleanField()					# Было ли разрешено отменить бой
	a_id=models.IntegerField(default=0, blank=True)				# BEGIN: Пользователь, который нападает
	a_kind=models.IntegerField(default=0, blank=True)
	a_attack=models.IntegerField(default=0, blank=True)				# BEGIN: Значения перед боем
	a_defence=models.IntegerField(default=0, blank=True)				
	a_honour=models.IntegerField(default=0, blank=True)				
	a_energy=models.IntegerField(default=0, blank=True)
	a_health=models.IntegerField()
	a_level=models.IntegerField()
	a_exp=models.IntegerField()
	a_silver=models.IntegerField()								# END: Значения перед боем
	a_n_attack=models.IntegerField(default=0, blank=True)			# BEGIN: Значения после боя
	a_n_defence=models.IntegerField(default=0, blank=True)				
	a_n_honour=models.IntegerField(default=0, blank=True)				
	a_n_energy=models.IntegerField(default=0, blank=True)
	a_n_health=models.IntegerField(default=0, blank=True)
	a_n_level=models.IntegerField(default=0, blank=True)
	a_n_exp=models.IntegerField(default=0, blank=True)
	a_n_silver=models.IntegerField(default=0, blank=True)		# END: Значения после боя
	d_id=models.IntegerField()									# BEGIN: Пользователь, на которого нападают
	d_kind=models.IntegerField()
	d_attack=models.IntegerField(default=0, blank=True)				# BEGIN: Значения перед боем
	d_defence=models.IntegerField(default=0, blank=True)				
	d_honour=models.IntegerField(default=0, blank=True)				
	d_energy=models.IntegerField(default=0, blank=True)
	d_health=models.IntegerField()
	d_level=models.IntegerField()
	d_exp=models.IntegerField()
	d_silver=models.IntegerField()								# END: Значения перед боем
	d_n_attack=models.IntegerField(default=0, blank=True)			# BEGIN: Значения после боя
	d_n_defence=models.IntegerField(default=0, blank=True)				
	d_n_honour=models.IntegerField(default=0, blank=True)				
	d_n_energy=models.IntegerField(default=0, blank=True)
	d_n_health=models.IntegerField(default=0, blank=True)
	d_n_level=models.IntegerField(default=0, blank=True)
	d_n_exp=models.IntegerField(default=0, blank=True)
	d_n_silver=models.IntegerField(default=0, blank=True)							# END: Значения после боя
	
	# Установка значений атакующего (a) и защищающегося (d) после боя
	def set_new_values(self, a, d):
		self.a_n_attack=a.attack
		self.a_n_defence=a.defence
		self.a_n_honour=a.honour
		self.a_n_energy=a.energy
		self.a_n_health=a.health
		self.a_n_level=a.level
		self.a_n_exp=a.exp
		self.a_n_silver=a.silver
		
		self.d_n_attack=d.attack
		self.d_n_defence=d.defence
		self.d_n_honour=d.honour
		self.d_n_energy=d.energy
		self.d_n_health=d.health
		self.d_n_level=d.level
		self.d_n_exp=d.exp
		self.d_n_silver=d.silver
		

# Почтовый ящик персонажа
class Mail(models.Model):
	to_chr_id = models.IntegerField() # Сделал не через ForeignKey, т.к. не давало сделать два форенкея на одну таблицу
	from_chr_id = models.ForeignKey(Character, null=True)	# Если NULL - то от системы. 
	created_at = models.DateTimeField(auto_now_add=True)
	txt=models.CharField(max_length=2000)

# Класс с вспомогательными методами
class Helper():
	@staticmethod
	def date_diff(first, second):
		return int(time.mktime(second.timetuple()) - time.mktime(first.timetuple()))