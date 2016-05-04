#!/bin/sh
if [ ! -d "~/.local/share/rhythmbox/plugins/" ]; then
    mkdir -p ~/.local/share/rhythmbox/plugins/
fi
cd ~/.local/share/rhythmbox/plugins/

if [ ! -d "./chromecast" ]; then
    git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
fi

cd chromecast/
git pull origin master
pip install -r requirements.txt
