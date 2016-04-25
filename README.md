#Rhythmbox plugin for Chromecast Support

The libs I want to use are:
- https://github.com/balloob/pychromecast
- http.server


##Installation: 
```bash
$ cd ~/.local/share/rhythmbox/plugins/
$ git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
$ cd chromecast/
$ pip install -r requirements.txt
```

Or copy and paste this script (source can be found [here](https://gist.github.com/KeizerDev/5ba4b0eca210338a6b80193771173a95)):

```bash
$ curl -s https://git.io/vwzJL | bash 
```

##Debugging:
If you want to improve or add something run `rhythmbox` from your terminal and you will see the python error log.
