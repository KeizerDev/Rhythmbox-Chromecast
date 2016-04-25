from urllib.parse import urlparse, unquote

from Utils import resolve_path, symlink_force


class ChromecastListeners:
    chromecastPlayer = None
    serverIp = "192.168.1.147"
    port = 8000

    def __init__(self, chromecastPlayer):
        self.chromecastPlayer = chromecastPlayer.media_controller

    def player_changed_cb(self, playing, entry):
        print("PLAY STATE CHANGED!")
        if playing:
            self.chromecastPlayer.play()
        else:
            self.chromecastPlayer.pause()

    def song_changed_cb(self, player, playing):
        # something is playing; get the track list from the play queue or the current playlists
        filename = unquote(urlparse(playing.get_playback_uri()).path).encode('utf8')
        symlink_force(filename, resolve_path('play.mp3'))

        self.chromecastPlayer.play_media('http://192.168.1.147:8000/', 'video/mp3')