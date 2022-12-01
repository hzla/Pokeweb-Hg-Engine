import ndspy
import ndspy.rom
import ndspy.narc
import code 
import io
import os
import os.path
from os import path
import json
import copy
import re

# code.interact(local=dict(globals(), **locals()))

######################### FILE SPECIFIC CONSTANTS #############################

def set_global_vars():
	global ROM_NAME, TYPES, CATEGORIES, EFFECT_CATEGORIES, EFFECTS, STATUSES, TARGETS, STATS, PROPERTIES, MOVE_NAMES, MOVES_NARC_FORMAT, RESULT_EFFECTS
	

	with open(f'session_settings.json', "r") as outfile:  
		settings = json.load(outfile) 
		ROM_NAME = settings['rom_name']

	TYPES = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel","Mystery", "Fire", "Water","Grass","Electric","Psychic","Ice","Dragon","Dark"]
	CATEGORIES = ["Physical","Special","Status"]

	EFFECT_CATEGORIES = ["No Special Effect", "Status Inflicting","Target Stat Changing","Healing","Chance to Inflict Status","Raising Target's Stat along Attack", "Lowering Target's Stat along Attack","Raise user stats","Lifesteal","OHKO","Weather","Safeguard", "Force Switch Out", "Unique Effect"]

	EFFECTS = open(f'texts/effects.txt', "r").read().splitlines() 

	STATUSES = ["None","Visible","Temporary","Infatuation", "Trapped"]

	TARGETS = ["Selected", "Depends", "Random", "Both", "Foes And Ally", "User", "User Side", "Active Field", "Opponents_Field", "Ally", "Acupressure", "Me First"]

	STATS = ["None", "Attack", "Defense", "Special Attack", "Special Defense", "Speed", "Accuracy", "Evasion", "All" ]

	PROPERTIES = ["contact","blocked_by_protect","reflected_by_magic_coat","stolen_by_snatch","copied_by_mirror_move","kings_rock","keep_hp_bar","hide_shadow"]

	MOVE_NAMES = open(f'texts/moves.txt', mode="r").read().splitlines()

	for i,move in enumerate(MOVE_NAMES):
		MOVE_NAMES[i] = re.sub(r'[^A-Za-z0-9 \-]+', '', move)


	RESULT_EFFECTS = open(f'Reference_Files/result_effects.txt', "r").read().splitlines()

	MOVES_NARC_FORMAT = [
	[2, "effect"],
	[1, "category"],
	[1, "power"],
	[1, 'type'],
	[1, "accuracy"],
	[1, "pp"],
	[1, "effect_chance"],
	[2, "target"],
	[1, "priority"],
	[1, "properties"],
	[1, "contest_effect"],
	[1, "contest_type"]]



#################################################################

def output_moves_json(narc):
	set_global_vars()
	data_index = 0
	for data in narc.files:
		data_name = data_index
		read_narc_data(data, MOVES_NARC_FORMAT, data_name)
		data_index += 1


def read_narc_data(data, narc_format, file_name):
	stream = io.BytesIO(data)
	move = {"raw": {}, "readable": {} }
	
	#USE THE FORMAT LIST TO PARSE BYTES
	for entry in narc_format: 
		move["raw"][entry[1]] = read_bytes(stream, entry[0])

	#CONVERT TO READABLE FORMAT USING CONSTANTS/TEXT BANKS
	move["readable"] = to_readable(move["raw"], file_name)
	
	#OUTPUT TO JSON
	if not os.path.exists(f'{ROM_NAME}/json/moves'):
		os.makedirs(f'{ROM_NAME}/json/moves')

	with open(f'{ROM_NAME}/json/moves/{file_name}.json', "w") as outfile:  
		json.dump(move, outfile) 


def to_readable(raw, file_name):
	readable = copy.deepcopy(raw)


	readable["index"] = file_name
	readable["animation"] = file_name
	if file_name >= len(MOVE_NAMES):
		readable["name"] = f'EXPANDED MOVE {file_name}'
		file_name = 0
		
	else:
		readable["name"]  = MOVE_NAMES[file_name] 




	
	readable["type"] = TYPES[raw["type"]]
	
	readable["category"] = CATEGORIES[raw["category"]]


	readable["effect"] = EFFECTS[raw["effect"]]


	# print(raw["target"])
	readable["target"] = raw["target"]


	index = 8
	binary_props = bin(raw["properties"])[2:].zfill(index) 
	
	for prop in PROPERTIES:
		amount = int(binary_props[index - 1])
		readable[prop] = amount
		index -= 1

	index = 12
	binary_props = bin(raw["target"])[2:].zfill(index) 
	
	for prop in TARGETS:
		amount = int(binary_props[index - 1])
		readable[prop] = amount
		index -= 1


	return readable

def read_bytes(stream, n):
	return int.from_bytes(stream.read(n), 'little')

	
