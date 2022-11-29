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
NARC_FILE_ID = 0
ROM_NAME = ""
BASE_ROM = ""

with open(f'session_settings.json', "r") as outfile:  
	settings = json.load(outfile) 
	ROM_NAME = settings['rom_name']
	BASE_ROM = settings["base_rom"]

LOCATIONS = open(f'texts/locations.txt', mode="r" ,encoding='utf-8').read().splitlines()

HEADER_LENGTH = 48

HEADER_NARC_FORMAT = [[1, "texture_1"],
[1, "texture_2"],
[2, "matrix"],
[2, "script"],
[2, "level_script"],
[2, "text_bank"],
[2, "music_day"],
[2, "music_night"],
[2, "event"],
[1, "location_name_id"],
[1, "name_style"],
[1, "weather"],
[1, "camera"],
[1, "follow_mode"],
[1, "flags"],
[1, "encounter"],
[1, "unknown"]]

#################################################################

## TODO instead of opening and editing the entire narc repeatedly, edit a variable 
## and edit the narc just once

def output_narc(narc_name="headers"):
	narcfile_path = f'{ROM_NAME}/narcs/{narc_name}-{NARC_FILE_ID}.narc'
	
	# ndspy copy of narcfile to edit
	
	narc = ndspy.narc.NARC.fromFile(narcfile_path)


	updated_narc = write_narc_data(HEADER_NARC_FORMAT, "headers")
	narc.files[0] = updated_narc
	
	old_narc = open(narcfile_path, "wb")
	old_narc.write(narc.save()) 

	print("narc saved")

def write_narc_data(narc_format, narc_name="headers"):
	file_path = f'{ROM_NAME}/json/{narc_name}/headers.json'
	
	stream = bytearray() # bytearray because is mutable

	with open(file_path, "r", encoding='ISO8859-1') as outfile:  	
		all_json_data = json.load(outfile)
		file_count = int(all_json_data["count"])

		for n in range(1, file_count + 1):
			for entry in narc_format:
				byte = write_bytes(stream, entry[0], all_json_data[str(n)][entry[1]])

	return stream


#slightly changed function for modifying a json file with all narc entries
def write_readable_to_raw(file_name, narc_name="headers"):
	data = {}
	json_file_path = f'{ROM_NAME}/json/{narc_name}/headers.json'

	with open(json_file_path, "r", encoding='ISO8859-1') as outfile:  	
		all_json_data = json.load(outfile)
		to_modify = all_json_data[str(file_name)]	
			
		if to_modify is None:
			return

		modified = to_raw(to_modify)
		all_json_data[str(file_name)] = modified

	with open(json_file_path, "w", encoding='ISO8859-1') as outfile: 
		json.dump(all_json_data, outfile)


def to_raw(readable):
	raw = copy.deepcopy(readable)
	raw["location_name_id"] = LOCATIONS.index(readable["location_name"])
	return raw
	

def write_bytes(stream, n, data):
	stream += (int(data).to_bytes(n, 'little'))		
	return stream



# ############### If run with arguments #############

if len(sys.argv) > 2 and sys.argv[1] == "update":

	file_names = sys.argv[2].split(",")
	 
	for file_name in file_names:
		write_readable_to_raw(int(file_name))
	