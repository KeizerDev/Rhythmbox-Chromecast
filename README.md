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

Or copy and paste this script (source can be found [here](https://github.com/KeizerDev/Rhythmbox-Chromecast/blob/master/setup.sh)):

```bash
$ curl -s https://git.io/vwzUw | bash 
```

##Debugging:
If you want to improve or add something run `rhythmbox` from your terminal and you will see the python error log.
