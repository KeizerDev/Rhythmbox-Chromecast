import operator
import socket

import time
import pychromecast
from gi.repository import RB, GObject, Gtk

import ChromecastListeners
import ChromecastServer

# try to load avahi, don't complain if it fails
import Prefs

try:
    import dbus
    import avahi

    use_mdns = True
except:
    use_mdns = False


class ChromecastSource(RB.Source):
    def __init__(self, **kwargs):
        super(ChromecastSource, self).__init__(kwargs)
        self.port = Prefs.port
        self.plugin = self.props.plugin
        self.player = None
        self.shell = None
        self.db = None
        self.entrygroup = None
        self.isPluginActivated = False
        self.isCastConnect = False
        self.chromecast = None
        self.chromecastPlayer = None
        self.chromecastListeners = None
        self.__entry_view = None

    def setup(self):
        if self.isPluginActivated:
            return

        shell = self.get_property("shell")
        player = shell.get_property("shell-player")

        self.shell = shell
        self.player = player
        self.db = shell.get_property("db")

        #self.chromecast = pychromecast.get_listed_chromecasts(friendly_names=Prefs.chromecastName)
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=Prefs.chromecastName)
        #[cc.device.friendly_name for cc in chromecasts]
        self.chromecast = chromecasts[0]
        self.chromecast.wait()
        self.chromecastPlayer = self.chromecast.media_controller

        self.chromecastListeners = ChromecastListeners.ChromecastListeners(self.chromecast)

        self.shell_cb_ids = (
            self.player.connect('playing-song-changed', self.chromecastListeners.song_changed_cb),
            self.player.connect('playing-changed', self.chromecastListeners.player_changed_cb)
        )

        self.draw_sidebar()


        model = self.get_property("query-model")
        playing_entry = player.get_playing_entry()
        # If the current playing entry is not in the playing source's
        # query model, we add temporarily to NP's query model so that
        # it appears in the sidebar and display page while the track
        # is playing. The track is removed from both views when it
        # stops playing (in the "song_changed_callback").
        # model.add_entry(["hallo", "Connected"], 1)
        # self.query_model.add_entry(entry, -1)

        iter = Gtk.TreeIter()
        if playing_entry and not model.entry_to_iter(playing_entry, iter):
            model.add_entry(playing_entry, 0)

        self.isPluginActivated = True

        self.server = ChromecastServer.ChromecastServer('', self.port, self)
        self._mdns_publish()


    def uninstall(self):
        self._mdns_withdraw()
        self.server.shutdown()
        self.server = None

        for id in self.shell_cb_ids:
            self.player.disconnect(id)

        self.player = None
        self.shell = None
        self.db = None

    def _mdns_publish(self):
        if use_mdns:
            bus = dbus.SystemBus()
            avahi_bus = bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
            avahi_svr = dbus.Interface(avahi_bus, avahi.DBUS_INTERFACE_SERVER)

            servicetype = '_http._tcp'
            servicename = 'Rhythmweb on %s' % (socket.gethostname())

            eg_path = avahi_svr.EntryGroupNew()
            eg_obj = bus.get_object(avahi.DBUS_NAME, eg_path)
            self.entrygroup = dbus.Interface(eg_obj,
                                             avahi.DBUS_INTERFACE_ENTRY_GROUP)
            self.entrygroup.AddService(avahi.IF_UNSPEC,
                                       avahi.PROTO_UNSPEC,
                                       0,
                                       servicename,
                                       servicetype,
                                       "",
                                       "",
                                       dbus.UInt16(self.port),
                                       ())
            self.entrygroup.Commit()

    def _mdns_withdraw(self):
        if use_mdns and self.entrygroup is not None:
            self.entrygroup.Reset()
            self.entrygroup.Free()
            self.entrygroup = None

    def draw_sidebar(self):
        shell = self.get_property("shell")
        sidebar = self.__sidebar = RB.EntryView.new(
            shell.get_property("db"),
            shell.get_property("shell-player"),
            True, True)

#        sidebar.set_property("vscrollbar-policy", Gtk.PolicyType.AUTOMATIC)
#        sidebar.set_property("shadow-type", Gtk.ShadowType.NONE)
        sidebar.get_style_context().add_class("nowplaying-sidebar")

        renderer = Gtk.CellRendererText.new()
        sidebar_column = self.__sidebar_column = Gtk.TreeViewColumn.new()
        sidebar_column.pack_start(renderer, True)
        sidebar_column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        sidebar_column.set_expand(True)
        sidebar_column.set_clickable(False)

        sidebar_column.set_cell_data_func(renderer, self.cell_data_func)

        sidebar.append_column_custom(
            sidebar_column, _("Chromecasts"),
            "Title", operator.gt, None)
        sidebar.set_columns_clickable(False)
        # super(ChromecastSource, self).setup_entry_view(sidebar)
        query_model = self.get_property("query-model")
        sidebar.set_model(query_model)
        shell.add_widget(sidebar, RB.ShellUILocation.RIGHT_SIDEBAR,
                         True, True)
        sidebar.set_visible(True)
        sidebar.show_all()
        # sidebar.
        # Connect to the "entry-activated" signal of the sidebar
        # sidebar.connect("entry-activated",
        #                 self.sidebar_entry_activated_callback)

        # Cell data func used by the sidebar to format the output of the entries.

    def cell_data_func(self, sidebar_column, renderer, tree_model, iter, data):
        db = self.get_property("shell").get_property("db")
        entry = tree_model.get(iter, 0)[0]
        title = entry[0]
        album = entry[1]
        markup = "<span size=\"smaller\">" + \
                 "<b>" + GObject.markup_escape_text(title) + "</b>\n" + \
                 "<i>" + GObject.markup_escape_text(album) + "</i></span>"
        renderer.set_property("markup", markup)
