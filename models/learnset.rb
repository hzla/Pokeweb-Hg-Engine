class Learnset < Pokenarc


	def self.write_data(data, batch=false)
		@@narc_name = "learnsets"
		@@upcases = []
		super
	end
end