import ndspy
import ndspy.rom, ndspy.codeCompression
import ndspy.narc
import code 
import io
import codecs
import os
import json
import sys
import msg_reader

from multiprocessing import Pool
import subprocess
from arm9_reader import output_tms_json

from pathlib import Path
import shutil



# code.interact(local=dict(globals(), **locals()))


#################### CREATE FOLDERS #############################
print("creating project folders")

narc_info = {} ##store narc names and file id pairs

with open(f'session_settings.json', "r") as outfile:  
	narc_info = json.load(outfile) 


rom_name = narc_info['rom_name'] 

# code.interact(local=dict(globals(), **locals()))

dirpath = Path(f'{rom_name}/json/moves')
print(dirpath) 
if dirpath.exists() and dirpath.is_dir():
    shutil.rmtree(dirpath)

if not os.path.exists(f'{rom_name}'):
	os.makedirs(f'{rom_name}')

for folder in ["narcs", "texts", "json"]:
	if not os.path.exists(f'{rom_name}/{folder}'):
		os.makedirs(f'{rom_name}/{folder}')



################# HARDCODED ROM INFO ##############################

BW_NARCS = [['a/0/3/7', "encounters"],
['a/0/0/2', 'personal'],
['a/0/3/3', 'learnsets'],
['a/0/1/1', 'moves'],
['a/0/3/4', 'evolutions'],
['a/0/5/5', 'trdata'],
['a/0/5/6', 'trpok'],
['a/0/2/8', 'hidden_abilities']] 
# ha in file index 7







NARCS = []
MSG_BANKS = []

################### EXTRACT RELEVANT NARCS AND ARM9 #######################

# MSG_BANKS = BW_MSG_BANKS
NARCS = BW_NARCS

print("extracting narcs")

with open(f'{rom_name.split("/")[-1]}.nds', 'rb') as f:
	data = f.read()

rom = ndspy.rom.NintendoDSRom(data)

for narc in NARCS:
	file_id = rom.filenames[narc[0]]
	file = rom.files[file_id]
	parsed_file = ndspy.narc.NARC(file)
	
	narc_info[narc[1]] = file_id # store file ID for later
	
	with open(f'{rom_name}/narcs/{narc[1]}-{file_id}.narc', 'wb') as f:
		f.write(file)


print("decompressing arm9")

arm9 = ndspy.codeCompression.decompress(rom.arm9)

with open(f'{rom_name}/arm9.bin', 'wb') as f:
	f.write(arm9)


# B2_SWARM_OFFSET = 0x00050bfc
# B2_GROTTO_ODDS_OFFSET = 0x00055218

################### EXTRACT RELEVANT TEXTS ##################
# print("parsing texts")

# msg_file_id = narc_info['message_texts']

# for msg_bank in MSG_BANKS:
# 	text = msg_reader.parse_msg_bank(f'{rom_name}/narcs/message_texts-{msg_file_id}.narc', msg_bank[0])
# 	with codecs.open(f'{rom_name}/texts/{msg_bank[1]}.txt', 'w', encoding='utf_8') as f:
# 		for block in text:
# 			for entry in block:
# 				try:
# 					f.write(entry)
# 				except UnicodeEncodeError:
# 					print("text parse error")
# 					# f.write(str(entry.encode("UTF-8")))
# 				f.write("\n")


##############################################################
################### WRITE SESSION SETTINGS ###################

settings = {}
settings.update(narc_info)
# settings["output_arm9"] = False
# settings["fairy"] = False



with open(f'session_settings.json', "w+") as outfile:  
	json.dump(settings, outfile) 

#############################################################
################### Provision Placeholders for alt form sprites ###########


# if narc_info["base_rom"] == "BW2":
# 	# sprites
# 	sprite_file_path = f'{rom_name}/narcs/sprites-{settings["sprites"]}.narc'
# 	narc = ndspy.narc.NARC.fromFile(sprite_file_path)
	
# 	with open(f'expansion_settings.json', "r") as outfile:  
# 		expansion_settings = json.load(outfile) 
# 		expansion = expansion_settings["moves"]

# 	if expansion > 0:
# 		moves_file_path = f'{rom_name}/narcs/moves-{settings["moves"]}.narc'
# 		animations_file_path = f'{rom_name}/narcs/move_animations-{settings["move_animations"]}.narc'
# 		b_animations_file_path = f'{rom_name}/narcs/battle_animations-{settings["battle_animations"]}.narc'

# 		moves = ndspy.narc.NARC.fromFile(moves_file_path)
# 		animations = ndspy.narc.NARC.fromFile(animations_file_path)
# 		b_animations = ndspy.narc.NARC.fromFile(b_animations_file_path)


		## Expand moves



# with open(f'{rom_name}/grotto_odds.bin', 'wb') as f:
# 	f.write(overlay36.data[B2_GROTTO_ODDS_OFFSET:(B2_GROTTO_ODDS_OFFSET + 200)])

# code.interact(local=dict(globals(), **locals()))


#############################################################

################### EXTRACT RELEVANT TEXTS ##################
# print("parsing texts")

# msg_file_id = narc_info['message_texts']

# for msg_bank in MSG_BANKS:
# 	text = msg_reader.parse_msg_bank(f'{rom_name}/narcs/message_texts-{msg_file_id}.narc', msg_bank[0])
# 	with codecs.open(f'{rom_name}/texts/{msg_bank[1]}.txt', 'w', encoding='utf_8') as f:
# 		for block in text:
# 			for entry in block:
# 				try:
# 					f.write(entry)
# 				except UnicodeEncodeError:
# 					print("text parse error")
# 					# f.write(str(entry.encode("UTF-8")))
# 				f.write("\n")

# 		# when using move id N > 673, b_animation_id (n - 561) is used
# 		# N must be greater than b_animations.files + moves.files = 559 + 114 = 673



# 		with open(f'session_settings.json', "w+") as outfile:  
# 			json.dump(settings, outfile) 

# 		# add filler moves

# settings = {}
# settings.update(narc_info)
# settings["output_arm9"] = False
# settings["fairy"] = False



# with open(f'session_settings.json', "w+") as outfile:  
# 	json.dump(settings, outfile) 

#############################################################
################### Provision Placeholders for alt form sprites ###########


# if narc_info["base_rom"] == "BW2":
# 	# sprites
# 	sprite_file_path = f'{rom_name}/narcs/sprites-{settings["sprites"]}.narc'
# 	narc = ndspy.narc.NARC.fromFile(sprite_file_path)
	
# 	with open(f'expansion_settings.json', "r") as outfile:  
# 		expansion_settings = json.load(outfile) 
# 		expansion = expansion_settings["moves"]

# 	if expansion > 0:
# 		moves_file_path = f'{rom_name}/narcs/moves-{settings["moves"]}.narc'
# 		animations_file_path = f'{rom_name}/narcs/move_animations-{settings["move_animations"]}.narc'
# 		b_animations_file_path = f'{rom_name}/narcs/battle_animations-{settings["battle_animations"]}.narc'

# 		moves = ndspy.narc.NARC.fromFile(moves_file_path)
# 		animations = ndspy.narc.NARC.fromFile(animations_file_path)
# 		b_animations = ndspy.narc.NARC.fromFile(b_animations_file_path)

# 		## Expand moves

# 		# when using move id N > 673, b_animation_id (n - 561) is used
# 		# N must be greater than b_animations.files + moves.files = 559 + 114 = 673

# 		settings["original_move_count"] = len(moves.files)
# 		settings["battle_animation_count"] = len(b_animations.files)
		
# 		with open(f'session_settings.json', "w+") as outfile:  
# 			json.dump(settings, outfile) 

# 		# add filler moves

# 		print(len(b_animations.files))

# 		for n in range(0, len(b_animations.files)):
# 			moves.files.append(moves.files[1])

# 		print(expansion)
# 		# expand animations and move files
# 		for n in range(0,expansion):
# 			n %= 559
# 			b_animations.files.append(animations.files[1])
# 			moves.files.append(moves.files[1])


# 		with open(moves_file_path, 'wb') as f:
# 			f.write(moves.save())

# 		with open(b_animations_file_path, 'wb') as f:
# 			f.write(b_animations.save())


# 	# code.interact(local=dict(globals(), **locals()))


# 	while len(narc.files) < 15080:
# 		narc.files.append(narc.files[-1])

# 	placeholder_sprites = narc.files[15000:15020]

	
# 	for n in range(100):
# 		narc.files += placeholder_sprites

# 	with open(f'{rom_name}/narcs/sprites-{settings["sprites"]}.narc', 'wb') as f:
# 		f.write(narc.save())

# 	# party icons 
# 	sprite_file_path = f'{rom_name}/narcs/icons-{settings["icons"]}.narc'
# 	narc = ndspy.narc.NARC.fromFile(sprite_file_path)

# 	while len(narc.files) < 1516:
# 		narc.files.append(narc.files[-1])

# 	placeholder_sprites = narc.files[1502:1504]

	
# 	for n in range(100):
# 		narc.files += placeholder_sprites

# 	with open(f'{rom_name}/narcs/icons-{settings["icons"]}.narc', 'wb') as f:
# 		f.write(narc.save())



	



#############################################################
####################CONVERT TO JSON #########################


os.system("python python/parallel.py")

output_tms_json(arm9)

