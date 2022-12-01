import ndspy
import ndspy.rom
import ndspy.narc
import code 
import io
import os
import json
import copy
import sys
import re

# code.interact(local=dict(globals(), **locals()))

######################### CONSTANTS #############################
NARC_FILE_ID = 263
with open(f'session_settings.json', "r") as outfile:  
	settings = json.load(outfile) 
	ROM_NAME = settings['rom_name']
	NARC_FILE_ID = settings["moves"]
	# ANIMATION_ID = settings["move_animations"]
	# B_ANIMATION_ID = settings["battle_animations"]

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

## TODO instead of opening and editing the entire narc repeatedly, edit a variable 
## and edit the narc just once

def output_narc(narc_name="moves"):
	json_files = os.listdir(f'{ROM_NAME}/json/moves')
	narcfile_path = f'{ROM_NAME}/narcs/{narc_name}-{NARC_FILE_ID}.narc'
	
	# ndspy copy of narcfile to edit
	narc = ndspy.narc.NARC.fromFile(narcfile_path)

	for f in json_files:
		file_name = int(f.split(".")[0])

		write_narc_data(file_name, MOVES_NARC_FORMAT, narc)

	old_narc = open(narcfile_path, "wb")
	old_narc.write(narc.save()) 

	print("narc saved")

def write_narc_data(file_name, narc_format, narc, narc_name="moves"):
	file_path = f'{ROM_NAME}/json/{narc_name}/{file_name}.json'
	narcfile_path = f'{ROM_NAME}/narcs/{narc_name}-{NARC_FILE_ID}.narc'

	stream = bytearray() # bytearray because is mutable

	with open(file_path, "r", encoding='ISO8859-1') as outfile:  	
		json_data = json.load(outfile)	

		#USE THE FORMAT LIST TO PARSE BYTES
		for entry in narc_format: 
			if entry[1] in json_data["raw"]:
				data = json_data["raw"][entry[1]]
				write_bytes(stream, entry[0], data)
	
	narc_entry_data = bytearray(narc.files[file_name])
	narc_entry_data[0:len(stream)] = stream
	narc.files[file_name] = narc_entry_data
	
def write_readable_to_raw(file_name, narc_name="moves"):
	data = {}
	json_file_path = f'{ROM_NAME}/json/{narc_name}/{file_name}.json'

	with open(json_file_path, "r", encoding='ISO8859-1') as outfile:  	
		json_data = json.load(outfile)	
			
		if json_data["readable"] is None:
			return
		new_raw_data = to_raw(json_data["readable"])
		json_data["raw"] = new_raw_data

	with open(json_file_path, "w", encoding='ISO8859-1') as outfile: 
		json.dump(json_data, outfile)

def to_raw(readable):
	raw = copy.deepcopy(readable)

	raw["type"] = TYPES.index(readable["type"].lower().capitalize())

	
	raw["category"] = CATEGORIES.index(readable["category"].lower().capitalize())
	# code.interact(local=dict(globals(), **locals()))
	raw["effect"] = EFFECTS.index(raw["effect"])


	binary_props = ""
	PROPERTIES.reverse()
	
	for prop in PROPERTIES:
		binary_props += bin(readable[prop])[2:].zfill(1)
	raw["properties"] = int(binary_props, 2)


	# # set animation
	# animations_file_path = f'{ROM_NAME}/narcs/move_animations-{ANIMATION_ID}.narc'
	# b_animations_file_path = f'{ROM_NAME}/narcs/battle_animations-{B_ANIMATION_ID}.narc'

	# # for non expanded moves
	# print(readable["index"])
	# if readable["index"] < 673:
	# 	print("no exp")
	# 	animations = ndspy.narc.NARC.fromFile(animations_file_path)
	# 	print(readable["index"])
	# 	animations.files[readable["index"]] = animations.files[readable["animation"]]
	# 	# code.interact(local=dict(globals(), **locals()))
	# 	with open(animations_file_path, 'wb') as f:
	# 		f.write(animations.save())

	# else: # for expanded moves
	# 	print("exp")
	# 	animations = ndspy.narc.NARC.fromFile(animations_file_path)
	# 	b_animations = ndspy.narc.NARC.fromFile(b_animations_file_path)
	# 	# code.interact(local=dict(globals(), **locals()))
	# 	b_animations.files[readable["index"] - 561] = animations.files[readable["animation"]]
	# 	with open(b_animations_file_path, 'wb') as f:
	# 		f.write(b_animations.save())

	return raw
	

def write_bytes(stream, n, data):
	stream += (int(data).to_bytes(n, 'little'))		
	return stream



################ If run with arguments #############

if len(sys.argv) > 2 and sys.argv[1] == "update":

	file_names = sys.argv[2].split(",")
	 
	for file_name in file_names:
		write_readable_to_raw(int(file_name))
	
	
# output_narc()

# write_readable_to_raw(1)
