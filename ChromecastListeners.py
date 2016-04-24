
def playing_changed_callback(self, CCplayer, playing):
    print("PLAY STATE CHANGED!")
    if playing:
        CCplayer.play()
    else:
        CCplayer.pause()

def song_changed_callback(self, player, entry):
    CCplayer.play_media('http://192.168.1.147:8000/play.mp3', 'video/mp3')
