from __future__ import print_function
from gi.repository import RB, GObject, Peas, Gtk, Gio, Gdk
import operator
import webbrowser
import pychromecast
import urllib.parse, urllib.request
import re


class ChromecastSource(RB.StaticPlaylistSource):
    def __init__(self, **kwargs):
        super(ChromecastSource, self).__init__(kwargs)
        self.__activated = False
        self.__playing_source = None
        self.__playing_source_signals = []
        self.__signals = []
        self.__filter = None
        self.__source_is_lib = False
        self.__song_count = 0
        self.__update_in_progress = False
        self.__queue_signal_id = None

    def setup(self):
        if self.__activated:
            return

        print("ACTIVATING SOURCE!")
        self.plugin = self.props.plugin
        self.__activated = True
        self.__entry_view = self.get_entry_view()
        self.__playing_source = None
        self.draw_sidebar()
        # self.setup_actions()

        signals = self.__signals
        shell = self.get_property("shell")
        player = shell.get_property("shell-player")
        signals.append((player.connect(
            "playing-source-changed",
            self.source_changed_callback),
                        player))

        # Activating Now Playing.
        playing_source = player.get_playing_source()
        # FIXME: Do not call the callback directly, move the common
        # code to a new method and call it in both places.
        self.source_changed_callback(player, playing_source)
        model = self.get_property("query-model")
        playing_entry = player.get_playing_entry()
        # If the current playing entry is not in the playing source's
        # query model, we add temporarily to NP's query model so that
        # it appears in the sidebar and display page while the track
        # is playing. The track is removed from both views when it
        # stops playing (in the "song_changed_callback").
        iter = Gtk.TreeIter()
        if playing_entry and not model.entry_to_iter(playing_entry, iter):
            model.add_entry(playing_entry, 0)
            signals.append((player.connect(
                "playing-song-changed",
                self.song_changed_callback,
                False),
                            player))
            self.update_titles()


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

        # Connect to the "entry-activated" signal of the sidebar
        # sidebar.connect("entry-activated",
        #                 self.sidebar_entry_activated_callback)

        # Cell data func used by the sidebar to format the output of the entries.

    def cell_data_func(self, sidebar_column, renderer, tree_model, iter, data):
        db = self.get_property("shell").get_property("db")
        entry = tree_model.get(iter, 0)[0]
        title = entry.get_string(RB.RhythmDBPropType.TITLE)
        artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
        album = entry.get_string(RB.RhythmDBPropType.ALBUM)
        markup = "<span size=\"smaller\">" + \
                 "<b>" + GObject.markup_escape_text(title) + "</b>\n" + \
                 "<i>" + GObject.markup_escape_text(album) + "</i>\n" + \
                 "<i>" + GObject.markup_escape_text(artist) + "</i></span>"
        renderer.set_property("markup", markup)

    
# self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
# self.__chromecast_player = self.__chromecast.media_controller


class Chromecast(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'ChromecastPlugin'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        shell = self.object
        # create Now Playing source
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