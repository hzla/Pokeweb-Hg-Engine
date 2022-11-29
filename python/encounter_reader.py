import ndspy
import ndspy.rom
import code 
import io
import os
import os.path
from os import path
import json
import copy
from math import floor

def set_global_vars():
	global LOCATIONS, ROM_NAME, ENCOUNTER_NARC_FORMAT, POKEDEX
	
	with open(f'session_settings.json', "r") as outfile:  
		settings = json.load(outfile) 
		ROM_NAME = settings['rom_name']




	POKEDEX = open(f'texts/pokedex.txt', "r").read().splitlines()

	ENCOUNTER_NARC_FORMAT = [
	[1, "walking_rate"],
	[1, "surf_rate"],
	[1, "rock_smash_rate"],
	[1, "old_rod_rate"],
	[1, "good_rod_rate"],
	[1, "super_rod_rate"],
	[2, "padding"]]

	for n in range(0,12):
		ENCOUNTER_NARC_FORMAT.append([1, f'walking_{n}_level'])

	for time in ["morning", "day", "night"]:
		for n in range(0,12):
			ENCOUNTER_NARC_FORMAT.append([2, f'{time}_{n}_species_id'])

	for region in ["hoenn", "sinnoh"]:
		for n in range(0,2):
			ENCOUNTER_NARC_FORMAT.append([2, f'{region}_{n}_species_id'])

	method_counts = [5,2,5,5,5]
	for idx, method in enumerate(["surf", "rock_smash", "old_rod", "good_rod", "super_rod"]):
		for n in range(0, method_counts[idx]):
			ENCOUNTER_NARC_FORMAT.append([1, f'{method}_{n}_min_lvl'])
			ENCOUNTER_NARC_FORMAT.append([1, f'{method}_{n}_max_lvl'])
			ENCOUNTER_NARC_FORMAT.append([2, f'{method}_{n}_species_id'])



def output_encounters_json(narc):
	set_global_vars()
	data_index = 0
	# code.interact(local=dict(globals(), **locals()))

	for data in narc.files:
		data_name = data_index
		read_narc_data(data, ENCOUNTER_NARC_FORMAT, data_name, "encounters")
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
	
	for time in ["morning", "day", "night"]:
		for n in range(0,12):
			mondata = get_form(raw[f'{time}_{n}_species_id'])
			readable[f'{time}_{n}_species_id'] = POKEDEX[mondata[1]]
			readable[f'{time}_{n}_species_form'] = mondata[0]


	for region in ["hoenn", "sinnoh"]:
		for n in range(0,2):
			mondata = get_form(raw[f'{region}_{n}_species_id'])
			readable[f'{region}_{n}_species_id'] = POKEDEX[mondata[1]]
			readable[f'{region}_{n}_species_form'] = mondata[0]

	method_counts = [5,2,5,5,5]
	for idx, method in enumerate(["surf", "rock_smash", "old_rod", "good_rod", "super_rod"]):
		for n in range(0, method_counts[idx]):
			ENCOUNTER_NARC_FORMAT.append([1, f'{method}_{n}_min_lvl'])
			ENCOUNTER_NARC_FORMAT.append([1, f'{method}_{n}_max_lvl'])
			
			mondata = get_form(raw[f'{method}_{n}_species_id'])
			readable[f'{method}_{n}_species_id'] = POKEDEX[mondata[1]]
			readable[f'{method}_{n}_species_form'] = mondata[0]
	return readable


def read_bytes(stream, n):
	return int.from_bytes(stream.read(n), 'little')

def get_form(species_id):
	if species_id < 1024:
		return [1, species_id]
	else:
		form = species_id // 1024
		base_form_id = raw[f'target_{n}'] - (1024 * form)
		return [form + 1, base_form_id]




	

