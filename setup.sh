#!/bin/bash
cd ~/.local/share/rhythmbox/plugins/
if [ ! -d "./chromecast" ]
    then
    git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
fi
cd chromecast/
pip install -r requirements.txt