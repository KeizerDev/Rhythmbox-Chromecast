# - encoding: utf8

from __future__ import print_function

from gi.repository import RB, GObject, Peas, Gtk, Gio

# self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
# self.__chromecast_player = self.__chromecast.media_controller
import ChromecastSource


class Chromecast(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'ChromecastPlugin'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        shell = self.object
        db = shell.props.db
        model = RB.RhythmDBQueryModel.new_empty(db)
        what, width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)
        self.source = GObject.new(
            ChromecastSource.ChromecastSource,
            name=_("Chromecast"),
            shell=shell,
            query_model=model,
            plugin=self
        )
        # source_group = RB.DisplayPageGroup.get_by_id("library")
        # shell.append_display_page(self.source, source_group)
        self.source.setup()
        # settings=settings,
        # shell.register_entry_type_for_source(self.source, entry_type)

    def do_deactivate(self):
        # destroy source
        self.source
        del self.source
