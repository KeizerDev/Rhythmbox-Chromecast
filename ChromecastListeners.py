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

    def song_changed_cb(self, entry, playing):
        self.chromecastPlayer.play_media('http://192.168.1.147:8000/', 'video/mp3')
