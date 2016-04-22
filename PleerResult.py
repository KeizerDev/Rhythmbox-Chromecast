class PleerResult:
	def __init__(self, entry):
		# Store the function. This will be called when we are ready to be added to the db.
		self.title = entry['song']
		self.artist = entry['artist']
		self.duration = int(entry['duration'])
		self.bitrate = entry['bitrate']
		self.url = entry['link']
