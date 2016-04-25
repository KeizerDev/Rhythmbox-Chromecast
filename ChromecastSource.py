import operator
import os
import socket

import pychromecast
from gi.repository import RB, GObject, Gtk

import ChromecastServer

# try to load avahi, don't complain if it fails
try:
    import dbus
    import avahi

    use_mdns = True
except:
    use_mdns = False


class ChromecastSource(RB.Source):
    def __init__(self, **kwargs):
        super(ChromecastSource, self).__init__(kwargs)
        self.port = 8000
        self.plugin = self.props.plugin
        self.__activated = False
        self.__isChromecastConnect = False
        self.__chromecast = None
        self.__chromecast_player = None
        self.__entry_view = None
        self.__signals = []
        self.player = None
        self.shell = None
        self.db = None

    def setup(self):
        # if self.__activated:
        #     return
        self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
        self.__chromecast.wait()
        self.__chromecast_player = self.__chromecast.media_controller
        self.__activated = True
        # self.__entry_view = self.get_entry_view()
        self.draw_sidebar()
        # self.setup_actions()


        shell = self.get_property("shell")
        player = shell.get_property("shell-player")

        self.shell = shell
        self.player = player
        self.db = shell.get_property("db")

        # Source change listener
        # self.__signals.append((player.connect("playing-source-changed", self.source_changed_callback), player))

        # PlayPause listener
        self.__signals.append((player.connect("playing-changed", self.playing_changed_callback), player))
        # Song Changed
        self.__signals.append((player.connect("playing-song-changed", self.song_changed_callback), player))

        # self.__signals.append((player.connect("volume-changed", self.volume_changed), player))

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

        self.server = ChromecastServer.ChromecastServer('', self.port, self)
        self._mdns_publish()

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

        sidebar.set_property("vscrollbar-policy", Gtk.PolicyType.AUTOMATIC)
        sidebar.set_property("shadow-type", Gtk.ShadowType.NONE)
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

    def playing_changed_callback(self, player, playing):
        print("PLAY STATE CHANGED!")
        # if self.__chromecast_player.status.content_id is None:
        #     self.__chromecast_player.play_media('http://192.168.1.147:8000/play.mp3', 'video/mp3')
        if playing:
            state = RB.EntryViewState.PLAYING
            self.__chromecast_player.play()
        else:
            state = RB.EntryViewState.PAUSED
            self.__chromecast_player.pause()

    def song_changed_callback(self, player, entry):
        self.__chromecast_player.play_media('http://192.168.1.147:8000/', 'video/mp3')
        path = os.path.split(entry.get_playback_uri())  # shell.props.shell_player.get_playing_entry().get_playback_uri()
        print("Allah" + path[0])

    def volume_changed(self, player, volume):
        print("ALLAH" + volume)
        self.__chromecast_player.play_media('http://192.168.1.147:8000/', 'video/mp3')
