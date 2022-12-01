import ndspy
import ndspy.rom
import ndspy.narc
import code 
import io
import os
import json
import copy
import sys


# code.interact(local=dict(globals(), **locals()))

######################### CONSTANTS #############################
def set_global_vars():
	global ROM_NAME, NARC_FORMAT, NARC_FILE_ID, POKEDEX, ITEMS, trpok, MOVES, GENDERS, TRAINER_FLAGS, FLAG_BINDINGS, FLAGS, POK_FLAG_BINDINGS, ABILITIES, NATURES
	
	with open(f'session_settings.json', "r") as outfile:  
		settings = json.load(outfile) 
		ROM_NAME = settings['rom_name']
		NARC_FILE_ID = settings["trpok"]


	TYPES = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel","Mystery", "Fire", "Water","Grass","Electric","Psychic","Ice","Dragon","Dark"]
	POKEDEX = open(f'texts/pokedex.txt', "r").read().splitlines()
	ITEMS = open(f'texts/items.txt', mode="r").read().splitlines()
	NATURES = open(f'texts/natures.txt', mode="r").read().splitlines()
	MOVES = open(f'texts/moves.txt', mode="r").read().splitlines()
	ABILITIES = open(f'texts/abilities.txt', mode="r").read().splitlines()
	GENDERS = ['Default', "Male", "Female"]
	FLAGS = ['status', 'hp', 'atk', 'def', 'spd', 'spatk', 'spdef', 'types', 'pp_counts', 'nickname']
	EXTRA_FLAGS = ['status', 'hp', 'atk', 'def', 'spd', 'spatk', 'spdef', 'type_1', 'type_2', 'move_1_pp','move_2_pp','move_3_pp','move_4_pp', 'nickname']

	TRAINER_FLAGS = ["has_moves", "has_items", "set_abilities", "set_ball", "set_iv_ev", "set_nature", "shiny_lock", "additional_flags"]

	FLAG_BINDINGS = {}
	

	POK_FLAG_BINDINGS = ['status', 'hp', 'atk', 'def', 'spd', 'spatk', 'spdef', 'types', 'move_1_pp', 'nickname']
	FLAG_BINDINGS = ["move_1", "item_id", "custom_ability", "ball", "hp_iv", "nature", "shiny_lock", "additional_flags"]


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
	[4, "status"],
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
	[1, "move_4_pp"]]

	# for n in range(0,11):
	# 	NARC_FORMAT.append([2, f'nickname_{n}'])

	NARC_FORMAT.append([2, 'ballseal'])

set_global_vars()
#################################################################


def output_narc(narc_name="trpok"):
	json_files = os.listdir(f'{ROM_NAME}/json/{narc_name}')
	narcfile_path = f'{ROM_NAME}/narcs/{narc_name}-{NARC_FILE_ID}.narc'
	
	# ndspy copy of narcfile to edit
	narc = ndspy.narc.NARC.fromFile(narcfile_path)

	for f in json_files:
		file_name = int(f.split(".")[0])

		write_narc_data(file_name, narc, narc_name)

	old_narc = open(narcfile_path, "wb")
	old_narc.write(narc.save()) 

	print("trpok narc saved")

def write_narc_data(file_name, narc, narc_name="trpok"):
	file_path = f'{ROM_NAME}/json/{narc_name}/{file_name}.json'
	narcfile_path = f'{ROM_NAME}/narcs/{narc_name}-{NARC_FILE_ID}.narc'

	stream = bytearray() # bytearray because is mutable

	with open(file_path, "r", encoding='ISO8859-1') as outfile:  	
		json_data = json.load(outfile)	

		narc_format = copy.deepcopy(NARC_FORMAT)


		trdata = json.load(open(f'{ROM_NAME}/json/trdata/{file_name}.json', "r"))["raw"]
		
		# remove unused trdata flag fields
		narc_format = adjust_narc_format(trdata, narc_format)
		# print(json_data)
		num_pokemon = json_data["readable"]["count"]

		if file_name == 496:
			print(narc_format)


		#USE THE FORMAT LIST TO PARSE BYTES
		for n in range(0, num_pokemon):
			pok_narc_format = copy.deepcopy(narc_format)


			
			# remove unused adiitional flag fields
			if [4, "additional_flags"] in pok_narc_format:
				pok_narc_format = adjust_pok_narc_format(json_data["raw"], pok_narc_format, n)

				if file_name == 496:
					print(pok_narc_format)
			
			for entry in pok_narc_format: 
				if f'{entry[1]}_{n}' in json_data["raw"]:
					data = json_data["raw"][f'{entry[1]}_{n}']
					write_bytes(stream, entry[0], data)

	if file_name >= len(narc.files):
		# narc_entry_data = bytearray()
		# narc_entry_data[0:len(stream)] = stream
		narc.files.append(stream)
	else:
		# narc_entry_data = bytearray(narc.files[file_name])
		# narc_entry_data[0:len(stream)] = stream
		narc.files[file_name] = stream
	
def write_readable_to_raw(file_name, narc_name="trpok"):
	data = {}
	json_file_path = f'{ROM_NAME}/json/{narc_name}/{file_name}.json'

	with open(json_file_path, "r", encoding='ISO8859-1') as outfile:  	
		json_data = json.load(outfile)	
			
		if json_data["readable"] is None:
			return

		tr_data = json.load(open(f'{ROM_NAME}/json/trdata/{file_name}.json', "r"))
		template = tr_data["raw"]["template"]

		new_raw_data = to_raw(json_data["readable"], template, tr_data)
		json_data["raw"] = new_raw_data[0]


		tr_data["raw"]["num_pokemon"] = json_data["readable"]["count"]
		tr_data["readable"]["num_pokemon"] = json_data["readable"]["count"]
		tr_data["raw"]["template"] = new_raw_data[1]

	with open(f'{ROM_NAME}/json/trdata/{file_name}.json', "w") as outfile:
		json.dump(tr_data, outfile)

	with open(json_file_path, "w", encoding='ISO8859-1') as outfile: 
		json.dump(json_data, outfile)

def to_raw(readable, template, trdata):
	raw = copy.deepcopy(readable)

	n = 0
	tr_flag_values = []
	tr_flags = 0

	while n < readable["count"]:
		if f'species_id_{n}' in raw:	

			form = raw[f'form_{n}']
			raw[f'species_id_{n}'] = ((form - 1) << 11 | POKEDEX.index(readable[f'species_id_{n}']))

			flag_values = []

			# set additional flags based on fields found with data
			for idx, flag in enumerate(POK_FLAG_BINDINGS):
				if f'{flag}_{n}' in raw:
					flag_values.append(1 << idx)
					# print(flag)

			if flag_values != []:
				additional_flags = 0
				for value in flag_values:
					additional_flags = additional_flags | value

				raw[f'additional_flags_{n}'] = additional_flags
				tr_flag_values.append(1 << 7)

			
			# set tr flags based on fields found with data

			if f'custom_ability_{n}' in raw:
				raw[ f'custom_ability_{n}'] = ABILITIES.index(raw[ f'custom_ability_{n}'].upper())

			if f'nature_{n}' in raw:
				raw[ f'nature_{n}'] = NATURES.index(raw[ f'nature_{n}'].upper())
			
			for idx, flag in enumerate(FLAG_BINDINGS):
				if f'{flag}_{n}' in raw:
					tr_flag_values.append(1 << idx)
					print(flag)


			for m in range(1,5):
				if f'move_{m}_{n}' in readable:
					raw[f'move_{m}_{n}'] = MOVES.index(readable[f'move_{m}_{n}'])
				else: 
					raw[f'move_{m}_{n}'] = 0


			if f'item_id_{n}' in readable:
				raw[f'item_id_{n}'] = ITEMS.index(readable[f'item_id_{n}'])
			else:
				raw[f'item_id_{n}'] = 0

			n += 1

	if tr_flag_values != []:
		for value in tr_flag_values:
			tr_flags = tr_flags | value
			print(tr_flags)

	return [raw, tr_flags]
	

def write_bytes(stream, n, data):
	stream += (int(data).to_bytes(n, 'little'))		
	return stream


def adjust_pok_narc_format(trpok, narc_format, trpok_index):
	flag_value = trpok[f"additional_flags_{trpok_index}"]
	flag_binary = bin(flag_value)[2:].zfill(10)

	if flag_binary[-1] != "1":
		narc_format.remove([4, "status"])

	if flag_binary[-2] != "1":
		narc_format.remove([2, "hp"])

	if flag_binary[-3] != "1":
		narc_format.remove([2, "atk"])

	if flag_binary[-4] != "1":
		narc_format.remove([2, "def"])

	if flag_binary[-5] != "1":
		narc_format.remove([2, "spd"])	
	
	if flag_binary[-6] != "1":
		narc_format.remove([2, "spatk"])	
	

	if flag_binary[-7] != "1":			
		narc_format.remove([2, "spdef"])
	
	if flag_binary[-8] != "1":			
		narc_format.remove([1, "type_1"])
		narc_format.remove([1, "type_2"])

	if flag_binary[-9] != "1":			
		for n in range(1,5):
			narc_format.remove([1, f"move_{n}_pp"])

	return narc_format


def adjust_narc_format(trdata, narc_format):
	flag_value = trdata["template"]
	flag_binary = bin(flag_value)[2:].zfill(10)

	if flag_binary[-1] != "1":
		for n in range(1,5):
			narc_format.remove([2, f"move_{n}"])

	if flag_binary[-2] != "1":
		narc_format.remove([2, "item_id"])

	if flag_binary[-3] != "1":
		narc_format.remove([2, "custom_ability"])

	if flag_binary[-4] != "1":
		narc_format.remove([2, "ball"])

	if flag_binary[-5] != "1":
		for value_type in ["iv", "ev"]:
			for stat in ["hp", "atk", "def", "spd", "spatk", "spdef"]:
				narc_format.remove([1, f'{stat}_{value_type}'])	
	
	if flag_binary[-6] != "1":			
		narc_format.remove([1, "nature"])

	if flag_binary[-7] != "1":			
		narc_format.remove([1, "shiny_lock"])
	
	if flag_binary[-8] != "1":			
		narc_format.remove([4, "additional_flags"])


	return narc_format

def get_form(species_id):
	if species_id < 2048:
		return [1, species_id]
	else:
		form = species_id // 2048
		base_form_id = raw[f'target_{n}'] - (2048 * form)
		return [form + 1, base_form_id]



################ If run with arguments #############

if len(sys.argv) > 2 and sys.argv[1] == "update":

	file_names = sys.argv[2].split(",")
	 
	for file_name in file_names:
		write_readable_to_raw(int(file_name))
	