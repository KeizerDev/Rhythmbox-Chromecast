import threading
import socket

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import PeasGtk
from gi.repository import Gio

import pychromecast
import rb

CHROMECAST_SCHEMA = 'org.gnome.rhythmbox.plugins.chromecast'


def get_lan_ip_address():
    addr = \
        [l for l in
         ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
             [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
              [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    return addr


class Preferences(GObject.Object, PeasGtk.Configurable):
    '''
    Preferences for the Chromecast Plugin. It holds the settings for
    the plugin.
    '''
    __gtype_name__ = 'ChromecastPreferences'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        '''
        Initialises the preferences, getting an instance of the settings saved
        by Gio.
        '''
        GObject.Object.__init__(self)

    def do_create_configure_widget(self):
        '''
        Creates the plugin's preferences dialog
        '''

        builder = Gtk.Builder()
        builder.add_from_file(rb.find_plugin_file(self,
                                                  'ui/chromecast_prefs.ui'))

        self._auto_ip = builder.get_object('auto_checkbutton')
        self._ip_entry = builder.get_object('ip_entry')
        self._ip_box = builder.get_object('ip_box')
        self._port_entry = builder.get_object('port_entry')

        self._find_button = builder.get_object('find_button')
        self._find_button.connect('clicked', self._find_button_clicked)
        self._chromecast_combobox = builder.get_object('chromecast_combobox')
        self._chromecast_liststore = builder.get_object('chromecast_liststore')
        self._save_button = builder.get_object('save_button')
        self._save_button.connect('clicked', self._save_button_clicked)

        self._settings = Gio.Settings.new(CHROMECAST_SCHEMA)
        self._auto_ip.set_active(self._settings['auto-ip'])
        self._auto_ip_changed()

        self._chromecast_liststore.append([self._settings['chromecast']])
        self._chromecast_combobox.set_active(0)

        self._auto_ip.connect('toggled', self._auto_ip_changed)

        return builder.get_object('main_box')

    def _auto_ip_changed(self, *args):
        if not self._auto_ip.get_active():
            ip = self._settings['ip']
            if ip == "":
                self._ip_entry.set_text(get_lan_ip_address())
            else:
                self._ip_entry.set_text(ip)

            port = self._settings['port']

            if port == "":
                self._port_entry.set_text('8000')
            else:
                self._port_entry.set_text(port)

        for child in self._ip_box.get_children():
            child.set_sensitive(not self._auto_ip.get_active())

    def _save_button_clicked(self, *args):
        self._settings['port'] = self._port_entry.get_text()
        self._settings['ip'] = self._ip_entry.get_text()
        self._settings['chromecast'] = self._chromecast_liststore.get_value(self._chromecast_combobox.get_active_iter(),0)
        self._settings['auto-ip'] = self._auto_ip.get_active()

    def _find_button_clicked(self, *args):
        self._find_button.set_sensitive(False)

        def get_chromecasts():
            chromecast_dict = pychromecast.get_chromecasts_as_dict()

            self._chromecast_liststore.clear()

            for key in chromecast_dict.keys():
                self._chromecast_liststore.append([key])

            if len(self._chromecast_liststore) > 0:
                self._chromecast_combobox.set_active(0)

            self._find_button.set_sensitive(True)

        thread = threading.Thread(target=get_chromecasts)
        thread.daemon = True
        thread.start()
