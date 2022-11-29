class Header

	def self.get_all
		file_path = "#{$rom_name}/json/headers/headers.json"
		data = JSON.parse(File.open(file_path, "r"){|f| f.read})
		data
	end

	def self.location_names
		file_path = "texts/locations.txt"
		data = File.open(file_path, "r:ISO8859-1"){|f| f.read}.split("\n").uniq
	end

	def self.find_location_by_map_id map_id
		headers = get_all
		location = nil
		headers.each do |k,v|
			next if k == "count"
			if v["map_id"] == map_id
				location = v["location_name"]
				break
			end
		end
		location
	end


	def self.write_batch_data data
		@@upcases = []
		data["file_names"].each do |file|
			data["file_name"] = file
			write_data(data)
		end
	end

	def self.write_data data, batch=false
		@@upcases = []
		if batch
			write_batch_data data
		end

		file_name = data["file_name"]
		field_to_change = data["field"]
		changed_value = data["value"]

		file_path = "#{$rom_name}/json/headers/headers.json"
		json_data = JSON.parse(File.open(file_path, "r"){|f| f.read})

		if data["int"]
			changed_value = changed_value.to_i
		end

		if data["field"] == "location_name"
			location_path = "#{$rom_name}/texts/locations.txt"
			location_names = File.open(location_path, "r:ISO8859-1"){|f| f.read}.split("\n")
			location_name_id = location_names.find_index(changed_value)
			json_data[file_name]['location_name_id'] = location_name_id
		end


		json_data[file_name][field_to_change] = changed_value
		File.open(file_path, "w") { |f| f.write json_data.to_json }
	end

	def self.expanded_fields
		col_1 = [[65535, "event"], [255, "texture_1"],[255, "texture_2"], [65535, "level_script_id"]]
		col_2 = [[255, "name_style" ], [255, "camera"], [255, "flags"], [255, "follow_mode"]]
		col_3 = [[65535, "music_day"], [65535,"music_night"], [255,"unknown"]]
		[col_1,col_2,col_3]
	end


end

