#!/bin/sh
f [ ! -d "~/.local/share/rhythmbox/plugins/" ]
    mkdir -p ~/.local/share/rhythmbox/plugins/
fi
cd ~/.local/share/rhythmbox/plugins/
f [ ! -d "./chromecast" ]
    then
    git clone https://github.com/KeizerDev/Rhythmbox-Chromecast.git chromecast
fi
cd chromecast/
git pull origin master
pip install -r requirements.txt
