import __builtin__

# Максимальный уровень игрока в игре
__builtin__.MAX_LEVEL = 3
# Максимальное значение фракции пользователя
__builtin__.MAX_FRACTION = 1

# Максимальное количество персонажей у игрока
__builtin__.MAX_CHARS = 8

# Количество игроков, которые доступны на арене
__builtin__.ARENA_CHR_CNT = 4
# Количество игроков, которые доступны для тренировки
__builtin__.TRAINING_CHR_CNT = 4

# Разница уровеней, которые могут драться между собой. Первое число - что надо вычесть из уровеня игрока, что б получить минимальный уровень, второе число - что надо прибавить, что б получить максимальный уровень
__builtin__.FIGHT_LEVEL_RANGE = [1,1]

# Максимальные значения, до которых можно прокачать параметры во время тренировки. В зависимости от рассы, типа и уровня
# Тройной массив: 1 уровень - расса (kind), 2 - уровень персонажа, 3 - конкретный параметр персонажа
__builtin__.MAX_TRAINING_VALUES = [
						[
							[100, 50], # атака, защита
							[150, 100],
							[200, 200],
						],
						[
							[50, 100], # атака, защита
							[100, 150],
							[200, 200],
						]
					]

# Значения прироста параметров персонажа в зависимости от рассы (первый уровень массива) и уровеня персонажа (второй уровень массива)
__builtin__.VALUES_INCS = [
						[
							[10, 10, 10, 10, 10, 0, 10, 10], # strength, adroitness, endurance, luck, will, honour, health, exp
							[20, 20, 20, 20, 20, 0, 10, 20], # strength, adroitness, endurance, luck, will, honour, health, exp
							[30, 30, 30, 30, 30, 0, 10, 30], # strength, adroitness, endurance, luck, will, honour, health, exp
						],
						[
							[10, 10, 10, 10, 10, 0, 10, 10], # strength, adroitness, endurance, luck, will, honour, health, exp
							[20, 20, 20, 20, 20, 0, 10, 20], # strength, adroitness, endurance, luck, will, honour, health, exp
							[30, 30, 30, 30, 30, 0, 10, 30], # strength, adroitness, endurance, luck, will, honour, health, exp
						]
					]

# Вычитание чести за выход из боя. Расса - первый уровень массива, уровень - второй уровень массива					
__builtin__.HONOUR_SUB = [
						[10,20,50],
						[10,20,50]
					]	

# Прибавление чести за выход из боя соперника. Расса - первый уровень массива, уровень - второй уровень массива					
__builtin__.HONOUR_INC = [
						[10,20,50],
						[10,20,50]
					]						

# Пороги экспы, после которых происходит левелап. Индекс массива - уровень, с которого переходят на следующий уровень					
__builtin__.EXP_TO_LEVELUP = [100, 200, 300]

# Экспа за победу, индекс - текущий уровень
__builtin__.EXP_FOR_WIN = [10, 20, 30]

# Серебро за победу, индекс - текущий уровень
__builtin__.SILVER_FOR_WIN = [100, 200, 300]

# Предустановки персонажей. Индекс массива - расса (kind)
__builtin__.BASE_CHARACTERS = [
								{"renewal":10, "village_level":0, "gold":100, "silver":1000, "crystal":0, "name":"Ninja", "strength": 20, "adroitness": 10, "endurance": 100, "luck": 100, "will": 100, "honour": 100, "health": 100, "energy":100, "exp":0, "level":0}, 
								{"renewal":10, "village_level":0, "gold":100, "silver":1000, "crystal":0, "name":"Samurai", "strength": 20, "adroitness": 10, "endurance": 100, "luck": 100, "will": 100, "honour": 100, "health": 100, "energy":100, "exp":0, "level":0}
							]

# Максимальный уровень здания (на 1 меньше, чем к-во элементов в массивах настроек, т.к. уровень начинается с 0)
__builtin__.MAX_BUILDING_LEVEL = 2

# Скорость производства в зданиях. Первый уровень массива - тип здания, воторой - уровень							
__builtin__.BUILDING_PRODUCE_SPEED = [
								[10, 20, 30],
								[10, 20, 30],
								[10, 20, 30],
								[10, 20, 30],
								[10, 20, 30],
								[10, 20, 30],
							]

# Максимумы производства в зданиях. Больше не могут произвести. Первый уровень массива - тип здания, воторой - уровень			
# 2012-08-22 Решил перенести все хранение в UserProfile (склад), поэтому ограничение хранения будет в STORE_MAXIMUMS											
__builtin__.BUILDING_PRODUCE_MAXIMUMS = [
								[100, 200, 300],
								[100, 200, 300],
								[100, 200, 300],
								[100, 200, 300],
								[100, 200, 300],
								[100, 200, 300],
							]
							
__builtin__.STORE_MAXIMUMS = [
								{'rice': 100, 'iron': 100},
								{'rice': 200, 'iron': 200},
								{'rice': 300, 'iron': 300},
							]

# Возрастание удачи при медитации. Первый уровень - левел чара, второй уровень: 0 - прирост в минуту, 1 - максимальное возможное значение							
__builtin__.LUCK_INCREASE = [
								[1,200],
								[2,300],
								[3,400],
						]
							
class BuildingTypes:
	FIELD=0
	MINE=1
	WORKSHOP=2
	GARDEN=3
	TEMPLE=4
	LIBRARY=5
	
class SlotTypes:
	MAIN=1
	THROWING=2
	CHEMISTRY=3

class FigthStatuses:
	STARTED=0
	FINISHED=1
	DISMISSED=2
	TIMEOUT=3

class MissionTypes:
	FIGHT=0
	GUARD_VILLAGE=1
	ATTACK_VILLAGE=2
	MEDITATION=3
	SEND_CARAVAN=4
	ATTACK_CARAVAN=5
	
# Количество пользователей, которые отображаются в списке в миссии "атака на деревню"
__builtin__.MISSION_ATTACK_VILLAGE_CNT = 2
# Значения минут, на которые можно посадить медитировать
__builtin__.MISSION_MEDITATION_MINS = [5,10,20]
