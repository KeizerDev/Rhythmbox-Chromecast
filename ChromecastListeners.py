from urllib.parse import urlparse, unquote

import Prefs
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

        self.chromecastPlayer.play_media(Prefs.server, 'video/mp3')