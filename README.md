#Rhythmbox plugin for Chromecast Support
##Project explanation
I was thinking of a setting under tools where I can lookup for available chromecasts and toggle the connection between them **(I'm not sure about the possibilities of that)**. Creating a new library(Like Rhythmbox-pleer is) is also okay but mabe too much for such a utility.

When I'm connected to a chromecast and I want to play a track, it should look to the player what path the music is and make it ready in the player but don't play it. The player should be insync of the chromecast instead of otherwise. The pc should be muted and the sound settings in Rhythmbox should be equal/listen to:  
```python
cast = pychromecast.get_chromecast(friendly_name="Living Room")
cast.volume(0.3)
```

It should also create a webserver and point it to the current playing file and send that to the chromecast when I'm connected to any. E.g.:
```python
mc = cast.media_controller
mc.play_media('http://192.168.0.3:8340/1. Pink floyd - Another Brick In The Wall.mp3', 'video/mp3')
```
(It can also be a Symbolic link to a certain dir so it can keep a standard file name like *play.mp3* )


The libs I want to use are:
- https://github.com/balloob/pychromecast
- http.server


##Installation: 
1. `$ cd ~/.local/share/rhythmbox/plugins`
2. `$ git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast`

OR  

You may just download repository [this](https://github.com/KeizerDev/Rhythmbox-Chromecast/archive/master.zip) and extract it in `~/.local/share/rhythmbox/plugins`

##Debugging:
If you want to improve or add something run `rhythmbox` from your terminal and you will see the python error log.
