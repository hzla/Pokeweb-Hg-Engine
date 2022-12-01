import ndspy
import ndspy.rom
import code 
import io
import os
import os.path
from os import path
import json
import copy


def set_global_vars():
	global ROM_NAME, NARC_FORMAT, POKEDEX, METHODS, ITEMS, MOVES
	
	with open(f'session_settings.json', "r") as outfile:  
		settings = json.load(outfile) 
		ROM_NAME = settings['rom_name']

	ITEMS = open(f'texts/items.txt', mode="r").read().splitlines()
	POKEDEX = open(f'texts/pokedex.txt', "r").read().splitlines()
	MOVES = open(f'texts/moves.txt', mode="r").read().splitlines()

	METHODS = open(f'Reference_Files/evo_methods.txt', mode="r").read().splitlines()

	NARC_FORMAT = []

	for n in range(0, 9):
		NARC_FORMAT.append([2, f'method_{n}'])
		NARC_FORMAT.append([2, f'param_{n}'])
		NARC_FORMAT.append([2, f'target_{n}'])

	
def output_evolutions_json(narc):
	set_global_vars()
	data_index = 0

	# while len(narc.files) < 800:
	# 	narc.files.append(narc.files[0])

	for data in narc.files:
		data_name = data_index
		read_narc_data(data, NARC_FORMAT, data_name, "evolutions")
		data_index += 1

def read_narc_data(data, narc_format, file_name, narc_name):
	stream = io.BytesIO(data)
	file = {"raw": {}, "readable": {} }

	#USE THE FORMAT LIST TO PARSE BYTES
	for entry in narc_format: 
		file["raw"][entry[1]] = read_bytes(stream, entry[0])

	#CONVERT TO READABLE FORMAT USING CONSTANTS/TEXT BANKS
	file["readable"] = to_readable(file["raw"], file_name)
	
	#OUTPUT TO JSON
	if not os.path.exists(f'{ROM_NAME}/json/{narc_name}'):
		os.makedirs(f'{ROM_NAME}/json/{narc_name}')

	with open(f'{ROM_NAME}/json/{narc_name}/{file_name}.json', "w") as outfile:  
		json.dump(file, outfile) 

def to_readable(raw, file_name):
	readable = copy.deepcopy(raw)

	for n in range(0,9):
		readable[f'method_{n}'] = METHODS[raw[f'method_{n}']]



		if (raw[f'target_{n}']) > 2048:
			# print(file_name)
			# print(raw)
			form = raw[f'target_{n}'] // 2048 
			base_form_id = raw[f'target_{n}'] - (2048 * form )
			readable[f'target_{n}'] = POKEDEX[base_form_id]
			readable[f'target_form_{n}'] = form + 1
		else:
			readable[f'target_{n}'] = POKEDEX[(raw[f'target_{n}'])]
			readable[f'target_form_{n}'] = 1



		if raw[f'method_{n}'] in [6,8,16,17,18,19]:
			readable[f'param_{n}'] = ITEMS[raw[f'param_{n}']]
		elif raw[f'method_{n}'] == 20:
			readable[f'param_{n}'] = MOVES[raw[f'param_{n}']]
		elif raw[f'method_{n}'] == 21:
			readable[f'param_{n}'] = POKEDEX[raw[f'param_{n}']]
		else:
			readable

	return readable


def read_bytes(stream, n):
	return int.from_bytes(stream.read(n), 'little')

	

