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
import math


def set_global_vars():
	global ROM_NAME, NARC_FORMAT, POKEDEX, ITEMS, TRDATA, MOVES, GENDERS, NARC_PATH, ABILITIES, NATURES, STATUSES, FLAGS
	
	with open(f'session_settings.json', "r") as outfile:  
		settings = json.load(outfile) 
		ROM_NAME = settings['rom_name']
		NARC_FILE_ID = settings['trpok']
		NARC_PATH = f'{ROM_NAME}/narcs/trpok-{NARC_FILE_ID}.narc'


	POKEDEX = open(f'texts/pokedex.txt', "r").read().splitlines()
	ITEMS = open(f'texts/items.txt', mode="r").read().splitlines()
	NATURES = open(f'texts/items.txt', mode="r").read().splitlines()
	MOVES = open(f'texts/moves.txt', mode="r").read().splitlines()
	ABILITIES = open(f'texts/abilities.txt', mode="r").read().splitlines()
	GENDERS = ['Default', "Male", "Female"]
	FLAGS = ['Nothing', 'Status', 'Hp', 'Atk', 'Def', 'Spd', 'Spatk', 'Spdef', 'Types', 'PP Counts', 'Nickname']



	NARC_FORMAT = [[1, "ivs"],
	[1, "ability"],
	[2, "level"],
	[2, "species_id"],
	[2, "item_id"],
	[2, "move_1"],
	[2, "move_2"],
	[2, "move_3"],
	[2, "move_4"],
	[2, "custom_ability"],
	[2, "ball"],
	[1, "hp_iv"],
	[1, "atk_iv"],
	[1, "def_iv"],
	[1, "spd_iv"],
	[1, "spatk_iv"],
	[1, "spdef_iv"],
	[1, "hp_ev"],
	[1, "atk_ev"],
	[1, "def_ev"],
	[1, "spd_ev"],
	[1, "spatk_ev"],
	[1, "spdef_ev"],
	[1, "nature"],
	[1, "shiny_lock"],
	[4, "additional_flags"],
	[1, "status"],
	[2, "hp"],
	[2, "atk"],
	[2, "def"],
	[2, "spd"],
	[2, "spatk"],
	[2, "spdef"],
	[1, "type_1"],
	[1, "type_2"],
	[1, "move_1_pp"],
	[1, "move_2_pp"],
	[1, "move_3_pp"],
	[1, "move_14_pp"]]

	for n in range(0,11):
		NARC_FORMAT.append([2, f'nickname_{n}'])

	NARC_FORMAT.append([2, 'ballseal'])



def output_trpok_json(trpok_info):
	set_global_vars()
	data_index = 0
	narc = ndspy.narc.NARC.fromFile(NARC_PATH)


	for data in narc.files:	
		data_name = data_index
		template = trpok_info[data_index][0]
		num_pokemon = trpok_info[data_index][1]
		narc_format = NARC_FORMAT

		read_narc_data(data, narc_format, data_name, "trpok", template, num_pokemon)
		data_index += 1

	print("trpok")

def read_narc_data(data, narc_format, file_name, narc_name, template, num_pokemon):
	stream = io.BytesIO(data)
	file = {"raw": {}, "readable": {} }
	
	if num_pokemon > 0:
		print(file_name)
		print(len(data) / num_pokemon)
		print(data)
	
	#USE THE FORMAT LIST TO PARSE BYTES
	
	for n in range(0, num_pokemon):
		for entry in narc_format: 
			file["raw"][f'{entry[1]}_{n}'] = read_bytes(stream, entry[0])

	#CONVERT TO READABLE FORMAT USING CONSTANTS/TEXT BANKS
	file["readable"] = to_readable(file["raw"], file_name, template, num_pokemon)
	file["readable"]["template"] = template
	
	#OUTPUT TO JSON
	if not os.path.exists(f'{ROM_NAME}/json/{narc_name}'):
		os.makedirs(f'{ROM_NAME}/json/{narc_name}')

	with open(f'{ROM_NAME}/json/{narc_name}/{file_name}.json', "w") as outfile:  
		json.dump(file, outfile) 


def to_readable(raw, file_name, template, num_pokemon):
	readable = copy.deepcopy(raw)

	readable["count"] = num_pokemon

	for n in range(0, num_pokemon):
		
		readable[f'species_id_{n}'] = POKEDEX[raw[f'species_id_{n}']]
		

		readable[f'custom_ability_{n}'] = ABILITIES[raw[f'custom_ability_{n}']]
		
		for m in range(1,5):
			readable[f'move_{m}_{n}'] = MOVES[raw[f'move_{m}_{n}']]


		readable[f'item_id_{n}'] = ITEMS[raw[f'item_id_{n}']]

		index = 11
		props = bin(raw[f"additional_flags_{n}"])[2:].zfill(index) 
		
		for prop in FLAGS:
			amount = int(props[index - 1])
			readable[prop] = amount
			index -= 1

	return readable


def read_bytes(stream, n):
	return int.from_bytes(stream.read(n), 'little')

	

