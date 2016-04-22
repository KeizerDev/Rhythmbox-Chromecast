import urllib
import urllib.parse
import urllib.request as urllib2
import json
import re


def parse_tracks(html):
	""" Parse HTML to retrieve listed tracks """
	records = json.loads(html.decode('utf8'))
	matches = {}
	matches['total'] = records['found'];
	matches['tracks'] = []
	
	for item in records['tracks'] :
		bitrateObj = re.search('\d+', item['bitrate'])
		bitrate = bitrateObj.group(0) if bitrateObj else 0
		details = {
			'artist': item['artist'], 
			'song': item['track'], 
			'duration': item['length'], 
			'bitrate': int(bitrate), 
			'link': item['file']
		}
		matches['tracks'].append(details)
	
	return(matches)

