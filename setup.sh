#!/bin/sh
cd ~/.local/share/rhythmbox/plugins/
if [ ! -d "./chromecast" ]
    then
    git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git Chromecast
fi
cd Chromecast/
pip install -r requirements.txt