from __future__ import print_function

import operator

import pychromecast
from gi.repository import RB, GObject, Peas, Gtk


class ChromecastSource(RB.StaticPlaylistSource):
    def __init__(self, **kwargs):
        super(ChromecastSource, self).__init__(kwargs)
        self.__activated = False
        self.__isChromecastConnect = False
        self.__chromecast = None
        self.__chromecast_player = None
        self.__entry_view = None
        self.__signals = []

    def setup(self):
        if self.__activated:
            return
        self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
        self.__chromecast_player = self.__chromecast.media_controller
        self.plugin = self.props.plugin
        self.__activated = True
        self.__entry_view = self.get_entry_view()
        self.draw_sidebar()
        # self.setup_actions()

        shell = self.get_property("shell")
        player = shell.get_property("shell-player")

        # Source change listener
        # self.__signals.append((player.connect("playing-source-changed", self.source_changed_callback), player))

        # PlayPause listener
        self.__signals.append((player.connect("playing-changed", self.playing_changed_callback), player))
        # Song Changed
        self.__signals.append((player.connect("playing-song-changed", self.song_changed_callback), player))
        self.__signals.append((player.connect("volume_changed", self.volume_changed), player))


        model = self.get_property("query-model")
        playing_entry = player.get_playing_entry()
        # If the current playing entry is not in the playing source's
        # query model, we add temporarily to NP's query model so that
        # it appears in the sidebar and display page while the track
        # is playing. The track is removed from both views when it
        # stops playing (in the "song_changed_callback").
        model.add_entry(["hallo", "Connected"], 1)
        self.query_model.add_entry(entry, -1)

        iter = Gtk.TreeIter()
        if playing_entry and not model.entry_to_iter(playing_entry, iter):
            model.add_entry(playing_entry, 0)

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
        super(ChromecastSource, self).setup_entry_view(sidebar)
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
        self.__chromecast_player.play_media('http://192.168.1.147:8000/play.mp3', 'video/mp3')

    def volume_changed(self, player, volume):
        print("ALLAH" + volume)
        self.__chromecast_player.play_media('http://192.168.1.147:8000/play.mp3', 'video/mp3')


# self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
# self.__chromecast_player = self.__chromecast.media_controller


class Chromecast(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'ChromecastPlugin'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        shell = self.object
        # create Chromecast source
        self.__source = GObject.new(
            ChromecastSource,
            shell=shell,
            entry_type=RB.RhythmDB.get_song_entry_type(),
            is_local=False,
            plugin=self,
            show_browser=False,
            name=_("Chromecast")
        )

        self.__source.setup()

    def do_deactivate(self):
        # destroy source
        self.__source.do_delete_thyself()
        del self.__source


GObject.type_register(ChromecastSource)
