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

	chrs_db = Character.objects.filter(user=request.user)
	user_profile = UserProfile.objects.get(pk=request.user)

	
	# Если у игрока меньше чаров, чем максимум чаров, то надо отоброжать пустые записи, в темплейте такое не смог реализовать, поэтому тут
	#empty = []
	#if (len(chrs) < MAX_CHARS):
	#	for i in range(1, MAX_CHARS-len(chrs)):
	#		empty.append(None)
	
	# Преобразую в массив, т.к. в исходный объект не удалось вставить другие записи
	chrs = []
	for i in range(0, len(chrs_db)):
			chrs.append(chrs_db[i])
			
	if (len(chrs) < MAX_CHARS):
		for i in range(len(chrs_db), MAX_CHARS):
			chrs.append(Character(fraction=-1))
	
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
	
	
	
	return render_to_response('main_2.html', {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'chrs':chrs, 'user_profile': user_profile, 'usr_name':request.user.username, 'selected_chr':selected_chr, 'slots':slots, 'BG_FILE': 'bg_village.png'})

def registration_form(request):
	if request.method == 'GET':
		return render_to_response('registration.html', {'PAGE_NAME':PAGE_NAMES[2], 'WORDS':WORDS}) # , 'CHR_FRACTIONS':CHR_FRACTIONS

def registration(request):
	if request.method == 'GET':
		qd = request.GET

		name = qd.get('name', None)
		mail = qd.get('mail', None)
		psw = qd.get('psw', None)
		
		fraction=0 # 2012-08-06 - решил откахаться от фракций #qd.get('fraction', None) # Фракция
		
		if (name == None or mail == None or psw == None or fraction == None):
			return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
		
		#if (int(fraction) < 0 or int(fraction) > MAX_FRACTION):
		#	return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':2}) # Расса игрока не правильная
		
		# Дефолтный чар
		default_chr = BASE_CHARACTERS[0] #BASE_CHARACTERS[int(fraction)]
		
		# Регистрация пользователя
		user = User.objects.create_user(name, mail, psw)
		profile = UserProfile(user=user, fraction=fraction, renewal=default_chr['renewal'], village_level=default_chr['village_level'], gold=default_chr['gold'], silver=default_chr['silver'], crystal=default_chr['crystal'], village_name=DEFAULT_VILLAGE_NAME + ' ' + name )

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
		#new_chr = Character(name=default_chr['name'], strength=default_chr['strength'], adroitness=default_chr['adroitness'], endurance=default_chr['endurance'], luck=default_chr['luck'], will=default_chr['will'], honour=default_chr['honour'], health=default_chr['health'], energy=default_chr['energy'], exp=default_chr['exp'], level=default_chr['level'], user=user, fraction=fraction)
		
		#new_chr.save()
		#try:
		#	new_chr.save()
		#except:
		#	return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':2})

		# Создание слотов для оружия на персонаже
		#slot1 = Slot(chr=new_chr, type_id = SlotTypes.MAIN)
		#slot2 = Slot(chr=new_chr, type_id = SlotTypes.THROWING)
		#slot3 = Slot(chr=new_chr, type_id = SlotTypes.CHEMISTRY)
		
		#try:
		#	slot1.save()
		#	slot2.save()
		#	slot3.save()
		#except:
		#	return render_to_response('error.js', {'ERROR_CODE':2,'ERROR_IDX':3})
		
		new_chr = Character.create_new_char(user)
		
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
	id = request.GET.get('id') # ID персонажа
	
	if (id == None):
		return HttpResponse('Choose character!')
	
	chr = Character.objects.get(pk=id)
	
	# Можно смотреть только своих персонажей
	if (chr.user_id != request.user.id):
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
		
	name = request.GET.get('new_name')
	
	# Надо сохранить новое имя
	if (name != None):
		check_chars = Character.objects.filter(user_id=request.user).exclude(pk=id).filter(name__exact=name)
		if (len(check_chars) > 0):
			return HttpResponse("ERROR: You have other character with the same name!")
			
		chr.name = name
		# TODO Обработка ошибки
		chr.save()
		
	
	return render_to_response('char_info.html', {'PAGE_NAME':PAGE_NAMES[3], 'WORDS':WORDS, 'chr':chr, 'BG_FILE': 'bg_village.png' })
	
@login_required()		
def add_new_character(request):
	chrs = Character.objects.filter(user=request.user)
	
	if (len(chrs) == MAX_CHARS):
		return HttpResponse("ERROR: Can't add new character. Maximum is reached.")
	
	res = Character.create_new_char(request.user)
	
	return HttpResponseRedirect("/")

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
		return render_to_response(bld_page, {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'bld':None, 'cnt':0, 'BG_FILE': 'bg_village.png'})
	
	# Сколько лежит на складе
	cnt = 0
	# Сколько произведено
	increase = 0
	# Сколько потеряно из-за переполнения склада
	lost = 0
	
	if (bld.type_id == BuildingTypes.FIELD or bld.type_id == BuildingTypes.MINE):
		user_profile = UserProfile.objects.get(pk=request.user)
		# Результат увеличения товара
		add_res = user_profile.add_to_store(bld)
		
		return HttpResponse(add_res)
		
		if (add_res != None):
			# TODO Обработка ошибки
			user_profile.save()
			bld.save()	# Сохраняется, что б изменилась дата последней проверки
			
			cnt = add_res['new']
			increase = add_res['increase']
			lost = add_res['lost']
		else:
			if (bld.type_id == BuildingTypes.FIELD):
				cnt = user_profile.rice
			elif (bld.type_id == BuildingTypes.MINE):
				cnt = user_profile.metal
		
	return render_to_response(bld_page, {'PAGE_NAME':PAGE_NAMES[1], 'WORDS':WORDS, 'bld':bld, 'cnt':cnt, 'increase': increase,  'lost': lost, 'BG_FILE': 'bg_village.png'})

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
	
	return render_to_response('missions.html', {'PAGE_NAME':PAGE_NAMES[4], 'WORDS':WORDS, 'chr_id':id, 'BG_FILE': 'bg_village.png'})
	
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
		
	#try:
	#	user_profile = UserProfile.objects.get(user=request.user)
	#except Building.DoesNotExist:
	#	return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':3})		
	
	#enemies = Character.objects.exclude(kind__exact=chr.kind).filter(id__gt=0)
	min_level = chr.level - FIGHT_LEVEL_RANGE[0]
	max_level = chr.level + FIGHT_LEVEL_RANGE[1]
	#enemies = Character.objects.raw("SELECT c.* FROM main_character c INNER JOIN main_userprofile p ON c.user_id = p.user_id WHERE p.fraction<>%s AND c.health > 0 AND c.level BETWEEN %s AND %s ORDER BY RAND() LIMIT %s", [user_profile.fraction, min_level, max_level, ARENA_CHR_CNT])
	# 2012-08-06 Отказ от фракций, так что бить можно всех, кроме персонажев того же пользователя
	#enemies = Character.objects.raw("SELECT * FROM main_character WHERE user_id<>%s AND health > 0 AND level BETWEEN %s AND %s ORDER BY RAND() LIMIT %s", [chr.user_id, min_level, max_level, ARENA_CHR_CNT])
	enemies = Character.objects.raw("SELECT c.*, u.village_name FROM main_character c INNER JOIN main_userprofile u ON c.user_id = u.user_id WHERE c.user_id<>%s AND c.health > 0 AND c.level BETWEEN %s AND %s AND (c.mission_id IS NULL OR (c.mission_finish_dt IS NOT NULL AND c.mission_finish_dt < NOW())) ORDER BY RAND() LIMIT %s", [chr.user_id, min_level, max_level, ARENA_CHR_CNT]) 
	
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
	return render_to_response('list.html', {'chrs':enemies, 'WORDS':WORDS, 'chr':chr, 'res_id':res_id, 'result':result, 'BG_FILE': 'bg_village.png'})

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
	
	fight_log = Fight(type=MissionTypes.FIGHT,enable_dismiss=enable_dismiss, a_user_id=chr_a.user_id, a_chr_id=chr_a.id, d_user_id=chr_d.user_id, d_chr_id=chr_d.id)
	fight_log.set_start_values(chr_a, chr_d)
	
	#battle_log = BattleLog(enable_dismiss=enable_dismiss, a_id=chr_a.id, a_kind=chr_a.kind, a_attack=chr_a.attack, a_defence=chr_a.defence, a_honour=chr_a.honour, a_energy=chr_a.energy, a_health = chr_a.health, a_level = chr_a.level, a_exp = chr_a.exp, a_silver = chr_a.silver,
	#						d_id=chr_d.id, d_kind=chr_d.kind, d_attack=chr_d.attack, d_defence=chr_d.defence, d_honour=chr_d.honour, d_energy=chr_d.energy, d_health = chr_d.health, d_level = chr_d.level, d_exp = chr_d.exp, d_silver = chr_d.silver)
	
	#battle_log.save()
	#return HttpResponse(str(fight_log.a_b_exp) + ' ' + str(fight_log.a_e_exp) + ' - ' + str(fight_log.d_b_exp) + ' ' + str(fight_log.d_e_exp))
	
	#fight_log.save()
	try:
		fight_log.save()
	except:
		return render_to_response('error.js', {'ERROR_CODE':3,'ERROR_IDX':3})
	
	return render_to_response('fight.html', {'PAGE_NAME':page_name, 'me':chr_a, 'enemy':chr_d, 'WORDS':WORDS, 'enable_dismiss':enable_dismiss, 'fight_id':fight_log.id, 'BG_FILE': 'bg_village.png'})
	
# Атака противника (расчет результата боя)
@login_required()
def attack(request):
	#if (request.user == None or request.user.is_anonymous()):
		#return render_to_response('error.js', {'ERROR_CODE':4})
	#	return HttpResponseRedirect("/")
		
	qd = request.GET
	id = qd.get('id', None) # ID боя
	
	if id is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
	
	fight_log = Fight.objects.get(pk=id)
	
	if (fight_log.status != FigthStatuses.STARTED):
		return render_to_response('error.js', {'ERROR_CODE':100,'ERROR_IDX':1}) # Бой уже завершен
	
	#Атакующий
	chr_a = Character.objects.get(pk=fight_log.a_chr_id)
	if (chr_a.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':5,'ERROR_IDX':1})
	
	# Защищающийся
	chr_d = Character.objects.get(pk=fight_log.d_chr_id)
	if (chr_d.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':6,'ERROR_IDX':1})
	
	res = fight_log.attack(chr_a, chr_d)
	# Для передачи на страницу результата
	result_response = 1
	result_name = WORDS[6]
	result_status = 'win'
	
	if (res < 0):
		result_response = -1
		result_name = WORDS[7]
		result_status = 'loss'
	
	
	fight_log.save()	
	chr_a.save()
	chr_d.save()
	
	#strength_dif_a = fight_log.a_e_strength - fight_log.a_b_strength
	#adroitness_dif_a = fight_log.a_e_adroitness - fight_log.a_b_adroitness
	#endurance_dif_a = fight_log.a_e_endurance - fight_log.a_b_endurance
	#luck_dif_a = fight_log.a_e_luck - fight_log.a_b_luck
	#will_dif_a = fight_log.a_e_will - fight_log.a_b_will
	#honour_dif_a = fight_log.a_e_honour - fight_log.a_b_honour
	#health_dif_a = fight_log.a_e_health - fight_log.a_b_health
	#energy_dif_a = fight_log.a_e_energy - fight_log.a_b_energy
	#exp_dif = fight_log.a_b_exp - fight_log.a_e_exp
	
	# TODO Изменение серебра и экспы в логе боя
	return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':result_name, 'status':result_status, 
				'strength_a':fight_log.diff_strength_a, 'adroitness_a':fight_log.diff_adroitness_a, 'endurance_a':fight_log.diff_endurance_a, 'luck_a':fight_log.diff_luck_a, 
				'will_a':fight_log.diff_will_a, 'honour_a':fight_log.diff_honour_a, 'health_a':fight_log.diff_health_a, 'energy_a':fight_log.diff_energy_a, 
				'exp_a':fight_log.diff_exp_a, 'strength_d':fight_log.diff_strength_d, 'adroitness_d':fight_log.diff_adroitness_d, 'endurance_d':fight_log.diff_endurance_d, 'luck_d':fight_log.diff_luck_d, 
				'will_d':fight_log.diff_will_d, 'honour_d':fight_log.diff_honour_d, 'health_d':fight_log.diff_health_d, 'energy_d':fight_log.diff_energy_d, 
				'exp_d':fight_log.diff_exp_d, 'chr_a_name': chr_a.name, 'chr_d_name': chr_d.name,
				'WORDS':WORDS, 'BG_FILE': 'bg_village.png'})

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
	
	#trace = 'IDs: a: ' + str(chr_a.id) + ', d: ' + str(chr_d.id)
	#trace += 'START: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	fight_log.dissmiss(chr_a, chr_d)
	
	#trace += 'FINISH: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	fight_log.save()
	chr_a.save()
	chr_d.save()
	
	#trace += 'AFTER SAVE: a: ' + str(chr_a.honour) + ', d: ' + str(chr_d.honour) + ';'
	
	#return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':WORDS[17], 'status':'dismiss', 'honour_sub':-1*honour_sub, 'WORDS':WORDS})
	return render_to_response('fight_result.html', {'PAGE_NAME':WORDS[18], 'status_name':WORDS[17], 'status':'dismiss', 'honour_a':fight_log.diff_honour_a, 'WORDS':WORDS, 'BG_FILE': 'bg_village.png', 'chr_a_name': chr_a.name, 'chr_d_name': chr_d.name})

@login_required()
def mission_start(request):
	qd = request.GET
	id = qd.get('id', None) # ID чара, который отправляется в миссию
	type = qd.get('type', None) # ID типа миссии
	save = qd.get('save', None) # Сохранение или предварительный селект
	
	if (save != None):
		try:
			save = int(save)
		except:
			save = 0
	
	if id is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
		
	if type is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':2})
	
	#Чар
	chr = Character.objects.get(pk=id)
	if (chr.health == 0):
		return render_to_response('error.js', {'ERROR_CODE':5,'ERROR_IDX':1})
	
	#return HttpResponse(MissionTypes.GUARD_VILLAGE)
	message = ''
	show_buttons = False
	mission = None
	
	if (chr.is_on_mission):
		message = PHRASES[0].replace('#char_name#', chr.name)
	else:
		if (int(type) == MissionTypes.GUARD_VILLAGE):
			if (save == 1): # Старт миссии
				mission = Mission(type=MissionTypes.GUARD_VILLAGE, user_id=chr.user_id, chr_id=chr.id, level=chr.level)
				
				mission.save_new(chr) # TODO обработка ошибки
				
				message = PHRASES[2].replace('#char_name#', chr.name)
			else: # Подгатовка к старту миссии
				show_buttons = True
				message = PHRASES[1].replace('#char_name#', chr.name)
		elif (int(type) == MissionTypes.ATTACK_VILLAGE):
			if (save == 1):
				attack=request.GET.get('attack')
				if (attack==None):
					return HttpResponse('ERROR: Choose vilage!')
					
				try:
					attack = int(attack)
				except:
					return HttpResponse('ERROR: Wrong vilage!')
				
				# list нужен, что б считать
				# http://stackoverflow.com/questions/2317452/django-count-rawqueryset
				defenders = list(Character.objects.raw('SELECT * FROM main_character WHERE user_id=%s and mission_type_id=%s and mission_finish_dt IS NULL' , [attack, MissionTypes.GUARD_VILLAGE]))
				guard_char = None
				
				# Если деревню кто-то охраняет, то выбирается игрок с макимальным уровнем, если несколько игроков максимального уровня, то выбирается с максимальным здоровьем
				if (len(defenders) > 0):
					guard_char = defenders[0]
					for d in defenders:
						# Если больше уровень или если уровень одинаковый, но больше здоровье
						if (d.level > guard_char.level or (d.level == guard_char.level and d.health > guard_char.health)):
							guard_char = d
							
					return HttpResponse(guard_char.name)
				
				
				
				return HttpResponse(len(defenders))
				message = ''
			else:
				#villages = UserProfile.objects.raw('SELECT * FROM main_userprofile WHERE user_id<>%s ORDER BY RAND() LIMIT %s ', [chr.user_id, MISSION_ATTACK_VILLAGE_CNT]) # Список других игроков
				# TODO Убрать, для тестов - фиксированный набор деревень
				villages = UserProfile.objects.raw('SELECT * FROM main_userprofile WHERE user_id in (7,9)') # Список других игроков
				return render_to_response('mission_list.html', {'PAGE_NAME':PAGE_NAMES[5], 'WORDS':WORDS, 'chr_id':chr.id, 'type': type, 'BG_FILE': 'bg_village.png', 'villages': villages, 'message': WORDS[58]})
		elif (int(type) == MissionTypes.MEDITATION):
			if (save == 1):
				mission = Mission(type=MissionTypes.MEDITATION, user_id=chr.user_id, chr_id=chr.id, level=chr.level)
				
				mission.save_new(chr) # TODO обработка ошибки
				
				message = PHRASES[10].replace('#char_name#', chr.name)
			else:
				show_buttons = True
				message = PHRASES[9]
				
				#return render_to_response('mission_meditation.html', {'PAGE_NAME':PAGE_NAMES[5], 'WORDS':WORDS, 'chr_id':chr.id, 'type': type, 'BG_FILE': 'bg_village.png', 'message': WORDS[59], 'selector': selector })
	
	return render_to_response('mission_start.html', {'PAGE_NAME':PAGE_NAMES[5], 'WORDS':WORDS, 'chr_id':chr.id, 'type': type, 'BG_FILE': 'bg_village.png', 'message':message, 'show_buttons': show_buttons})

@login_required()
def mission_end(request):
	qd = request.GET
	id = qd.get('id', None) # ID чара, которому хочеться завершить миссию
	
	cancel = qd.get('cancel', None) # Сохранение или предварительный селект
	
	if (cancel != None):
		try:
			cancel = int(cancel)
		except:
			cancel = 0
	
	if id is None:
		return render_to_response('error.js', {'ERROR_CODE':1,'ERROR_IDX':1})
		
	#Чар
	chr = Character.objects.get(pk=id)
	
	message = ''
	show_buttons = False
	if (chr.is_on_mission == 0):
		message = PHRASES[3].replace('#char_name#', chr.name)
	elif (chr.is_on_mission == 1):
		message = PHRASES[4].replace('#char_name#', chr.name)
	else:
		if (cancel==1): # Сама отмена
			mission = Mission.objects.get(pk=chr.mission_id)  # TODO Обработка ошибки
			res = mission.cancel(chr) # TODO Обработка ошибки
			if (mission.type == MissionTypes.MEDITATION):
				message = PHRASES[11].replace('#char_name#', chr.name).replace('#mins#', str(res["mins"])).replace('#luck_change#', str(res["luck_change"])).replace('#old_luck#', str(res["old_luck"])).replace('#new_luck#', str(res["new_luck"]))
			else:
				message = PHRASES[6].replace('#char_name#', chr.name)
		else:
			message = PHRASES[5].replace('#char_name#', chr.name)
			show_buttons = True
	
	return render_to_response('mission_end.html', {'PAGE_NAME':PAGE_NAMES[6], 'WORDS':WORDS, 'chr_id':chr.id, 'type': type, 'BG_FILE': 'bg_village.png', 'message':message, 'show_buttons': show_buttons})
	
def test_headers(request):
	qd = request.META
	x_up_devcap_screenpixels = qd.get('X-UP-devcap-screenpixels', '')
	x_screen_width = qd.get('X-Screen-Width', '') 
	x_screen_height = qd.get('X-Screen-Height', '')
	ua_pixels = qd.get('UA-pixels', '')
	
	return render_to_response('test.html', {'agent': request.META["HTTP_USER_AGENT"], 'languages': request.META["HTTP_ACCEPT_LANGUAGE"], 'encodings':request.META["HTTP_ACCEPT_ENCODING"], 'x_up_devcap_screenpixels':x_up_devcap_screenpixels, 'x_screen_width':x_screen_width, 'x_screen_height':x_screen_height, 'ua_pixels':ua_pixels } )
	
def get_style(request, width, height):
	return HttpResponse("div.test { width: " + width + "px; height: " + height + " x; background-color: #ff0000; }")