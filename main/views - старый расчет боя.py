from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import QueryDict
from main.models import *
from django.db.models import Avg, Max, Min, Count, Sum

import settings
from settings import BuildingTypes, SlotTypes, FigthStatuses, MissionTypes
import dictionary

import random

# Декоратор, который определяет, залогинен пользователь или нет
def login_required():
	def _dec(view_func):
		def _view(request, *args, **kwargs):
			if (request.user == None or request.user.is_anonymous()):
				return HttpResponseRedirect("/")
			else:
				return view_func(request, *args, **kwargs)

		return _view
	return _dec

def start(request):
	if (request.user == None or request.user.is_anonymous()):
		return render_to_response('login.html', {'PAGE_NAME':PAGE_NAMES[0], 'WORDS':WORDS})

	chrs = Character.objects.filter(user=request.user)

	# Если у игрока меньше чаров, чем максимум чаров, то надо отоброжать пустые записи, в темплейте такое не смог реализовать, поэтому тут
	empty = []
	if (len(chrs) < MAX_CHARS):
		for i in range(1, MAX_CHARS-len(chrs)):
			empty.append(None)

	
	# Чар, которого надо сейчас показывать
	qd = request.GET
	id = qd.get('id', None) # ID, кого атакует
	selected_chr = chrs[0]
	if (id != None):
		for c in chrs:
			if (c.id == int(id)):
				selected_chr = c
				break
	
	# Слоты выбранного перса
	slots = Slot.objects.filter(chr=selected_chr)
	
	return render_to_response('main.html', {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'chrs':chrs, 'usr_name':request.user.username, 'empty':empty, 'selected_chr':selected_chr, 'slots':slots})

def registration_form(request):
	if request.method == 'GET':
		return render_to_response('registration.html', {'PAGE_NAME':PAGE_NAMES[2], 'WORDS':WORDS, 'CHR_FRACTIONS':CHR_FRACTIONS})

def registration(request):
	if request.method == 'GET':
		qd = request.GET

		name = qd.get('name', None)
		mail = qd.get('mail', None)
		psw = qd.get('psw', None)
		
		fraction= qd.get('fraction', None) # Фракция
		
		if (name == None or mail == None or psw == None or fraction == None):
			return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
		
		if (int(fraction) < 0 or int(fraction) > MAX_FRACTION):
			return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':2}) # Расса игрока не правильная
		
		# Дефолтный чар
		default_chr = BASE_CHARACTERS[int(fraction)]
		
		# Регистрация пользователя
		user = User.objects.create_user(name, mail, psw)
		profile = UserProfile(user=user, fraction=fraction, renewal=default_chr['renewal'], village_level=default_chr['village_level'], gold=default_chr['gold'], silver=default_chr['silver'], crystal=default_chr['crystal'] )

		# Поле в деревне
		field = Building(user=user, type_id=BuildingTypes.FIELD)
		
		try:
			user.save()
			profile.save()
			field.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
		
		#return HttpResponse(user.profile.fraction)
		
		# Создание персонажа
		new_chr = Character(name=default_chr['name'], strength=default_chr['strength'], adroitness=default_chr['adroitness'], endurance=default_chr['endurance'], luck=default_chr['luck'], will=default_chr['will'], honour=default_chr['honour'], health=default_chr['health'], energy=default_chr['energy'], exp=default_chr['exp'], level=default_chr['level'], user=user)
		
		new_chr.save()
		try:
			new_chr.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':2})

		# Создание слотов для оружия на персонаже
		slot1 = Slot(chr=new_chr, type_id = SlotTypes.MAIN)
		slot2 = Slot(chr=new_chr, type_id = SlotTypes.THROWING)
		slot3 = Slot(chr=new_chr, type_id = SlotTypes.CHEMISTRY)
		
		try:
			slot1.save()
			slot2.save()
			slot3.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':3})
		
		# Создание приветственного письма
		mail = Mail(to_chr_id = new_chr.id, txt = 'Hello, bro!')
		try:
			mail.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':5})
		
		
		return HttpResponseRedirect("/")

def login(request):
	if request.method == 'GET':
		qd = request.GET
		name = qd.get('name', None)
		psw = qd.get('psw', None)
		
		user = auth.authenticate(username=name, password=psw)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				
				#return render_to_response('OK.js')
				return HttpResponseRedirect("/")
			else:
				return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':1})
		else:
			return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':2})

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect("/")

@login_required()	
def char(request):
	qd = request.GET
	id = qd.get('id', None) # ID персонажа
	
	chr = Character.objects.get(pk=id)
	
	# Можно смотреть только своих персонажей
	if (chr.user_id != request.user.id):
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
	
	return render_to_response('char_info.html', {'PAGE_NAME':PAGE_NAMES[3], 'WORDS':WORDS, 'chr':chr})

# Здания в деревне
@login_required()	
def place(request, type):
	type_id = -1
	bld_page = ''
	
	if (type=='field'):
		type_id = BuildingTypes.FIELD 		# Поле риса
		bld_page = 'field.html'
	elif (type=='mine'):
		type_id = BuildingTypes.MINE		# Шахта	
		bld_page = 'mine.html'
	elif (type=='workshop'):
		type_id = BuildingTypes.WORKSHOP	# Мастерская
		bld_page = 'workshop.html'
	elif (type=='garden'):
		type_id = BuildingTypes.GARDEN		# Сад
		bld_page = 'garden.html'
	elif (type=='temple'):
		type_id = BuildingTypes.TEMPLE		# Храм
		bld_page = 'temple.html'
	elif (type=='library'):
		type_id = BuildingTypes.LIBRARY		# Библиотека
		bld_page = 'library.html'
	else:
		return HttpResponseRedirect("/") # Передали непонятно что
	
	bld	= None
	try: 
		bld = Building.objects.get(user=request.user, type_id=type_id)
	except Building.DoesNotExist:
		pass
	except:
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
	
	# Если здания еще нет
	if (bld == None):
		return render_to_response(bld_page, {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'bld':None, 'cnt':0})
	
	old_cnt = bld.cnt
	cnt = bld.recount()
	
	if (old_cnt != cnt):
		try:
			bld.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
		
	return render_to_response(bld_page, {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'bld':bld, 'cnt':cnt})

# Строительство здания
@login_required()
def build(request, type):
	type_id = -1
	
	if (type=="mine"):
		type_id = BuildingTypes.MINE
	elif (type=="workshop"):
		type_id = BuildingTypes.WORKSHOP
	elif (type=="garden"):
		type_id = BuildingTypes.GARDEN
	elif (type=="temple"):
		type_id = BuildingTypes.TEMPLE
	elif (type=="library"):
		type_id = BuildingTypes.LIBRARY
	else:
		return HttpResponseRedirect("/") # Передали непонятно что
	
	bld	= None
	try: 
		bld = Building.objects.get(user=request.user, type_id=type_id)
	except Building.DoesNotExist:
		pass
	except:
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
		
	# Если здание уже есть
	if (bld != None):
		return HttpResponseRedirect("/" + type + "/") 
		
	#return HttpResponse(type_id)
	bld = Building(user=request.user, type_id=type_id, level=0, cnt=0)
	bld.save()
	try:
		bld.save()
	except:
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
		
	return HttpResponseRedirect("/" + type + "/")

# Увеличение уровня здания
@login_required()
def improve(request, type):
	type_id = -1
	
	if (type=='field'):
		type_id = BuildingTypes.FIELD
	elif (type=='mine'):
		type_id = BuildingTypes.MINE
	elif (type=="workshop"):
		type_id = BuildingTypes.WORKSHOP
	elif (type=="garden"):
		type_id = BuildingTypes.GARDEN
	elif (type=="temple"):
		type_id = BuildingTypes.TEMPLE
	elif (type=="library"):
		type_id = BuildingTypes.LIBRARY
	else:
		return HttpResponseRedirect("/") # Передали непонятно что
	
	bld	= None
	try: 
		bld = Building.objects.get(user=request.user, type_id=type_id)
	except Building.DoesNotExist:
		return HttpResponseRedirect("/" + type + "/")  # Если здания нет, то возвращаем на страницу здания
	except:
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
	
	if (bld.level < MAX_BUILDING_LEVEL):
		bld.level += 1
		try:
			bld.save()
		except:
			return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
		
	return HttpResponseRedirect("/" + type + "/")

# Миссии для персонажа
@login_required()
def missions(request):
	qd = request.GET
	id = qd.get('id', None) # ID персонажа
	
	if (id == None):
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
	
	return render_to_response('missions.html', {'PAGE_NAME':PAGE_NAMES[4], 'WORDS':WORDS, 'chr_id':id})
	
# Список сообщений
@login_required()
def mail_list(request):
	#if (request.user == None or request.user.is_anonymous()):
	#	return render_to_response('error.js', {'ERROR_CODE':4})
	
	chr = Character.objects.get(pk=request.user.id)
	mails = Mail.objects.filter(to_chr_id=chr.id).order_by("-created_at")
	
	return render_to_response('mail_list.js', {'mails':mails})

# Список людей для нападения (из другой рассы)
@login_required()
def enemy_list(request):
	qd = request.GET
	id = qd.get('id', None) # ID персонажа
	
	if (id == None):
		return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':1})
	
	try:
		chr = Character.objects.get(pk=id)
	except Building.DoesNotExist:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':1})

	if (chr.user_id != request.user.id):
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':2})
		
	try:
		user_profile = UserProfile.objects.get(user=request.user)
	except Building.DoesNotExist:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':3})		
	
	#enemies = Character.objects.exclude(kind__exact=chr.kind).filter(id__gt=0)
	min_level = chr.level - FIGHT_LEVEL_RANGE[0]
	max_level = chr.level + FIGHT_LEVEL_RANGE[1]
	enemies = Character.objects.raw("SELECT c.* FROM main_character c INNER JOIN main_userprofile p ON c.user_id = p.user_id WHERE p.fraction<>%s AND c.health > 0 AND c.level BETWEEN %s AND %s ORDER BY RAND() LIMIT %s", [user_profile.fraction, min_level, max_level, ARENA_CHR_CNT])
	
	result = ""
	res_id = 0;
	try:
		res_id = int(request.GET.get('result', None))
		if (res_id != None):
			if (res_id == -1):
				result = WORDS[7]
			elif (res_id == 1):
				result = WORDS[6]
	except:
		pass
	#return render_to_response('chr_list.js', {'chrs':enemies})
	return render_to_response('list.html', {'chrs':enemies, 'chr':chr, 'res_id':res_id, 'result':result})

# Список людей для тренировки (из тойже рассы)	
@login_required()
def sparring_partner_list(request):
	#if (request.user == None or request.user.is_anonymous()):
		#return render_to_response('error.js', {'ERROR_CODE':4})
	#	return HttpResponseRedirect("/")
		
	chr = Character.objects.get(pk=request.user.id)
	min_level = chr.level - FIGHT_LEVEL_RANGE[0]
	max_level = chr.level + FIGHT_LEVEL_RANGE[1]
	#partners = Character.objects.filter(kind__exact=chr.kind).filter(id__gt=0).exclude(id__exact=chr.id)
	partners = Character.objects.raw("SELECT * FROM main_character WHERE id<>%s AND kind=%s AND health > 0 AND level BETWEEN %s AND %s ORDER BY rand() LIMIT %s", [chr.id, chr.kind, min_level, max_level, TRAINING_CHR_CNT])
	
	result = ""
	res_id = 0;
	try:
		res_id = int(request.GET.get('result', None))
		if (res_id != None):
			if (res_id == -1):
				result = WORDS[7]
			elif (res_id == 1):
				result = WORDS[6]
	except:
		pass
	
	#return render_to_response('chr_list.js', {'chrs':partners})
	return render_to_response('list.html', {'chrs':partners, 'me':chr, 'res_id':res_id, 'result':result})

# Страница перед боем
@login_required()
def fight(request):
	#if (request.user == None or request.user.is_anonymous()):
	#	return HttpResponseRedirect("/")
		
	qd = request.GET
	id_from = qd.get('id_from', None) # ID, кто атакует
	id_to = qd.get('id_to', None) # ID, кого атакует
	
	if id_from is None or id_to is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
	
	# Нельзя атоковать самого себя
	if id_from == id_to:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':2})
	
	# Атакующий
	try:
		chr_a = Character.objects.get(pk=id_from)
	except Building.DoesNotExist:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':1})

	# Нападающий не из чаров пользователя
	if (chr_a.user_id != request.user.id):
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':2})	
		
	# Мало здоровья у атакующего
	if (chr_a.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':5,'ERROR_IDX':1})
	
	# Защищающийся
	try:
		chr_d = Character.objects.get(pk=id_to)
	except Building.DoesNotExist:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':2})
	
	# Попытка напасть на своего чара
	if (chr_a.user_id == chr_d.user_id):
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':10})	
		
	# Мало здоровья у защищающегося
	if (chr_d.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':6,'ERROR_IDX':1})
	
	# Бой невозможен - слишком большой разброс уровней игроков
	if (chr_d.level < chr_a.level - FIGHT_LEVEL_RANGE[0] or chr_d.level > chr_a.level + FIGHT_LEVEL_RANGE[1]):
		return render_to_response('error.js', {'ERROR_CODE':7,'ERROR_IDX':1}) 
	
	page_name = WORDS[8] # Бой
	#if (chr_a.kind == chr_d.kind):
	#	page_name = WORDS[9] # Тренировка
		
	enable_dismiss = (chr_a.level < chr_d.level) # and chr_a.kind != chr_d.kind
	
	fight_log = Fight(enable_dismiss=enable_dismiss, a_user_id=chr_a.user_id, a_chr_id=chr_a.id, d_user_id=chr_d.user_id, d_chr_id=chr_d.id)
	fight_log.set_start_values(chr_a, chr_d)
	
	#battle_log = BattleLog(enable_dismiss=enable_dismiss, a_id=chr_a.id, a_kind=chr_a.kind, a_attack=chr_a.attack, a_defence=chr_a.defence, a_honour=chr_a.honour, a_energy=chr_a.energy, a_health = chr_a.health, a_level = chr_a.level, a_exp = chr_a.exp, a_silver = chr_a.silver,
	#						d_id=chr_d.id, d_kind=chr_d.kind, d_attack=chr_d.attack, d_defence=chr_d.defence, d_honour=chr_d.honour, d_energy=chr_d.energy, d_health = chr_d.health, d_level = chr_d.level, d_exp = chr_d.exp, d_silver = chr_d.silver)
	
	#battle_log.save()
	
	try:
		fight_log.save()
	except:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':3})
	
	return render_to_response('fight.html', {'PAGE_NAME':page_name, 'me':chr_a, 'enemy':chr_d, 'WORDS':WORDS, 'enable_dismiss':enable_dismiss, 'fight_id':fight_log.id})
	
# Атака противника (расчет результата боя)
@login_required()
def attack(request):
	#if (request.user == None or request.user.is_anonymous()):
		#return render_to_response('error.js', {'ERROR_CODE':4})
	#	return HttpResponseRedirect("/")
		
	qd = request.GET
	id = qd.get('id', None) # ID, кого атакует
	
	if id is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
	#return HttpResponse(request.user.id)
	
	battle_log = BattleLog.objects.get(pk=id)	
	
	if (battle_log.status > 0):
		return render_to_response('error.js', {'ERROR_CODE':100,'ERROR_IDX':1}) # Бой уже завершен
	
	#Атакующий
	chr_a = Character.objects.get(pk=battle_log.a_id)
	if (chr_a.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':5,'ERROR_IDX':1})

	# Защищающийся
	chr_d = Character.objects.get(pk=battle_log.d_id)
	if (chr_d.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':6,'ERROR_IDX':1})
		
	chr_a_weight = chr_a.get_weight();
	chr_d_weight = chr_d.get_weight();
	win_pr = float(chr_a_weight) / (chr_a_weight + chr_d_weight)
	
	# Результат. Если  > 0 - то победа, < 0 - поражение. Значение по модулю - коэффициент урона проигравшему
	# Если res > 0, то чем больше, тем уверенее победа
	# Если res < 0, то чем больше по модулю, тем сильнее поражение
	res = win_pr - random.random();
	
	if (res < 0 and abs(res) < 0.01):
		res = -0.01
	elif (res >= 0 and res < 0.01):
		res = 0.01
	
	#return HttpResponse(chr_a.get_max_training_values_inc())

	# Бой с другой рассой
	if chr_a.kind != chr_d.kind:
		# Коэфициенты увеличения параметров победившего
		koef = [1, 1] # Атака, оборона
		
		winner = chr_a
		loser = chr_d
		# Для передачи на страницу результата
		result_response = 1
		result_name = WORDS[6]
		result_status = 'win'
		# Победил атакующий
		if (res < 0):
			winner = chr_d
			loser = chr_a
			result_response = -1
			result_name = WORDS[7]
			result_status = 'loss'
			
		winner_values_inc = winner.get_values_inc()
		loser_values_inc = loser.get_values_inc()
		
		abs_res = abs(res)
		winner.attack = winner.attack + int(winner_values_inc[0] * koef[0])
		winner.defence = winner.defence + int(winner_values_inc[1] * koef[1])
		#winner.p3 = winner.p3 + int(winner_values_inc[2] * koef[2])
		#return HttpResponse("Бой: " + str(res) + " Winner: " + str(winner.id) + " Loser: " + str(loser.id))	
		# Если не очень уверенная победа, то у нападавшего тоже уменьшается здоровье
		if (abs_res < 0.5):
			winner.health = int(winner.health*(0.5+abs_res))
				
		winner.add_exp_and_silver_for_win()
		
		loser.health = int(loser.health*abs_res)
			
		winner.save()
		loser.save()
		
		battle_log.set_new_values(chr_a, chr_d)
		battle_log.status=1
		battle_log.res = res
		battle_log.save()
		
		attack_dif = battle_log.a_n_attack - battle_log.a_attack
		defence_dif = battle_log.a_n_defence - battle_log.a_defence
		health_dif = battle_log.a_n_health - battle_log.a_health
		exp_dif = battle_log.a_n_exp - battle_log.a_exp
		level_dif = battle_log.a_n_level - battle_log.a_level
		silver_dif = battle_log.a_n_silver - battle_log.a_silver
		
		return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':result_name, 'status':result_status, 'attack':attack_dif, 'defence':defence_dif, 'health':health_dif, 'exp':exp_dif, 'level':level_dif, 'silver':silver_dif, 'WORDS':WORDS})
		#return HttpResponseRedirect("/enemy_list/?result=" + str(result_response))
		#return HttpResponse("Бой: " + str(res) + " Способность к атаке " + str(chr_a.p1) + " Способность к защите " + str(chr_a.p2) + " Способность к восстановлению " + str(chr_a.p3) + " Здоровье: " + str(chr_a.health) + " Экспа: " + str(chr_a.exp) + " Уровень: " + str(chr_a.level))
	# Бой со своей рассой - тренировка
	else:
		# Максимальные значения, до которых можно прокачать себя во время тренировки, в зависимости от уровня
		# атака, оборона
		maximums = chr_a.get_max_training_values_inc()
		
		# Коэфициенты при поражении
		koef = [0.5, 0.5] # Атака, оборона
		
		# Для передачи обратно в список игроков
		result_response = -1
		result_name = WORDS[7]
		result_status = 'loss'
		if (res > 0):
			koef = [1.3, 1.3] # Атака, оборона
			result_response = 1
			result_name = WORDS[6]
			result_status = 'win'
			
		chr_a_values_inc = chr_a.get_values_inc()
			
		# Увеличение атаки
		if (chr_a.attack < maximums[0]):
			chr_a.attack = chr_a.attack + int(chr_a_values_inc[0] * koef[0])
			chr_a.attack = maximums[0] if (chr_a.attack > maximums[0]) else chr_a.attack
		# Увеличение защиты
		if (chr_a.defence < maximums[1]):
			chr_a.defence = chr_a.defence + int(chr_a_values_inc[1] * koef[1])
			chr_a.defence = maximums[1] if (chr_a.defence > maximums[1]) else chr_a.defence
		# Увеличение защиты
		#if (chr_a.p3 < maximums[2]):
		#	chr_a.p3 = chr_a.p3 + int(chr_a_values_inc[2] * koef[2])
		#	chr_a.p3 = maximums[2] if (chr_a.p3 > maximums[2]) else chr_a.p3	
		
		chr_a.save()
		
		battle_log.set_new_values(chr_a, chr_d)
		battle_log.status=1
		battle_log.res = res
		battle_log.save()
		
		attack_dif = battle_log.a_n_attack - battle_log.a_attack
		defence_dif = battle_log.a_n_defence - battle_log.a_defence
		health_dif = battle_log.a_n_health - battle_log.a_health
		exp_dif = battle_log.a_n_exp - battle_log.a_exp
		level_dif = battle_log.a_n_level - battle_log.a_level
		silver_dif = battle_log.a_n_silver - battle_log.a_silver
		
		return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':result_name, 'status':result_status, 'attack':attack_dif, 'defence':defence_dif, 'health':health_dif, 'exp':exp_dif, 'level':level_dif, 'silver':silver_dif, 'WORDS':WORDS})
		#return HttpResponseRedirect("/sp_list/?result=" + str(result_response))
		#return HttpResponse("Тренировка: " + str(res) + " Способность к атаке " + str(chr_a.p1) + " Способность к защите " + str(chr_a.p2) + " Способность к восстановлению " + str(chr_a.p3))
	
	
	return render_to_response('OK.js')

@login_required()
def dismiss(request):
	#if (request.user == None or request.user.is_anonymous()):
	#	return HttpResponseRedirect("/")
		
	qd = request.GET
	id = qd.get('id', None) # ID боя
	
	if id is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
	
	fight_log = Fight.objects.get(pk=id)	
	
	if (fight_log.status != FigthStatuses.STARTED):
		return render_to_response('error.js', {'ERROR_CODE':100,'ERROR_IDX':1}) # Бой уже завершен
	
	chr_a = Character.objects.get(pk=fight_log.a_chr_id)
	chr_d = Character.objects.get(pk=fight_log.d_chr_id)
	
	trace = 'IDs: a: ' + str(chr_a.id) + ', d: ' + str(chr_d.id)
	trace += 'START: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	fight_log.dissmiss(chr_a, chr_d)
	
	trace += 'FINISH: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	fight_log.save()
	chr_a.save()
	chr_d.save()
	
	trace += 'AFTER SAVE: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	#return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':WORDS[17], 'status':'dismiss', 'honour_sub':-1*honour_sub, 'WORDS':WORDS})
	return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':WORDS[17], 'status':'dismiss', 'honour_sub':fight_log.diff_honour_a, 'WORDS':WORDS})
	
def test_headers(request):
	qd = request.META
	x_up_devcap_screenpixels = qd.get('X-UP-devcap-screenpixels', '')
	x_screen_width = qd.get('X-Screen-Width', '') 
	x_screen_height = qd.get('X-Screen-Height', '')
	ua_pixels = qd.get('UA-pixels', '')
	
	return render_to_response('test.html', {'agent': request.META["HTTP_USER_AGENT"], 'languages': request.META["HTTP_ACCEPT_LANGUAGE"], 'encodings':request.META["HTTP_ACCEPT_ENCODING"], 'x_up_devcap_screenpixels':x_up_devcap_screenpixels, 'x_screen_width':x_screen_width, 'x_screen_height':x_screen_height, 'ua_pixels':ua_pixels } )
	
def get_style(request, width, height):
	return HttpResponse("div.test { width: " + width + "px; height: " + height + " x; background-color: #ff0000; }")