<h1 align="center">Rhythmbox Chromecast</h1>
<p align="center">Stream all your local music to your Chromecast (Audio).</p>

<p align="center">
    <a href="http://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/npm/l/express.svg">
    </a>    
</p>

----

<h2 align="center">Installation:</h2>
<p align="center">
Run <a href="https://github.com/KeizerDev/Rhythmbox-Chromecast/blob/master/setup.sh">this</a> script:
</p>
```bash
$ wget -O - https://git.io/vwzUw | bash
```
<p align="center">
Or 
</p>
```bash
$ cd ~/.local/share/rhythmbox/plugins/
$ git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
$ cd chromecast/
$ pip install -r requirements.txt
```

<b>Ubuntu Installation (14.04 and later)</b>

```
sudo apt install python3-pip
mkdir -p ~/.local/share/rhythmbox/plugins/
cd ~/.local/share/rhythmbox/plugins/
git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
sudo pip3 install -r requirements.txt
```


After that you have to update the `Prefs.py` file with your preferred settings. This is a quick fix because of the lack of a decent GUI. **Will be fixed soon!**

Milestones: 
- [x] Connect to a Chromecast.
- [x] Play/Pause music with button/media buttons.
- [x] Send local music to your chromecast.
- [ ] Create a GUI where you can select/connect to your chromecast.
- [ ] Create a settings menu for port and ip settings.
- [ ] Create support for other plugins that are not local.
- [ ] Listen to Rhythmbox volume manager and change it on the chromecast.
- [ ] Mute rhythmbox locally (or give option to do so).
 
Optional:
- [ ] Create support for multiple chromecasts


**Known bugs:**
- When starting Rhythmbox with the plugin or when you enable it, it will freeze for a while. This because it will auto connect to the chromecast you've filled in the Prefs.py file. This will be fixed when we have a GUI.

### Contributors

* [Robert-Jan Keizer (KeizerDev)](https://github.com/KeizerDev/)

### License

Rhythmbox-Chromecast is released under the MIT license.