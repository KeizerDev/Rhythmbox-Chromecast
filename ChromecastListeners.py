from urllib.parse import urlparse, unquote

from gi.repository import Gio

#import Prefs
from ChromecastPrefs import CHROMECAST_SCHEMA
from ChromecastPrefs import get_lan_ip_address

from Utils import resolve_path, symlink_force


class ChromecastListeners:
    chromecastPlayer = None

    def __init__(self, chromecastPlayer):
        self.chromecastPlayer = chromecastPlayer.media_controller

    def player_changed_cb(self, player, playing):
        print("PLAY STATE CHANGED!")
        if playing:
            self.chromecastPlayer.play()
        else:
            self.chromecastPlayer.pause()

    def song_changed_cb(self, player, entry):
        # something is playing; get the track list from the play queue or the current playlists
        filename = unquote(urlparse(entry.get_playback_uri()).path).encode('utf8')
        symlink_force(filename, resolve_path('play.mp3'))

        self._settings = Gio.Settings.new(CHROMECAST_SCHEMA)

        if self._settings['auto-ip']:
            server = get_lan_ip_address()
        else:
            server = self._settings['ip']

        self.chromecastPlayer.play_media("http://{}:{}/".format(server, self._settings['port']), 'video/mp3')
