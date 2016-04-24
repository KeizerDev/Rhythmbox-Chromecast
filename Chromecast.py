from __future__ import print_function

from gi.repository import RB, GObject, Peas, Gtk, Gio


# self.__chromecast = pychromecast.get_chromecast(friendly_name="RobsKamerMuziek")
# self.__chromecast_player = self.__chromecast.media_controller

class ChromecastEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name='chromecast')

    def do_can_sync_metadata(self, entry):
        return True


class Chromecast(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'ChromecastPlugin'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        shell = self.object
        db = shell.props.db
        model = RB.RhythmDBQueryModel.new_empty(db)
        entry_type = ChromecastEntryType()
        db.register_entry_type(entry_type)
        what, width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)
        iconfile = Gio.File.new_for_path(self.plugin_info.get_module_dir() + "/chromecast.svg")
        source_group = RB.DisplayPageGroup.get_by_id("library")

        # schema_src = Gio.SettingsSchemaSource.new_from_directory(self.plugin_info.get_module_dir(),
        #                                                          Gio.SettingsSchemaSource.get_default(), False)
        # schema = schema_src.lookup('org.gnome.rhythmbox.plugins.pleer', False)
        # settings = Gio.Settings.new_full(schema, None, None)

        self.source = GObject.new(ChromecastSource, name=_("Chromecast"), shell=shell, query_model=model, plugin=self,
                                  entry_type=entry_type, icon=Gio.FileIcon.new(iconfile)) # settings=settings,
        shell.append_display_page(self.source, source_group)
        shell.register_entry_type_for_source(self.source, entry_type)

        self.source.setup()

    def do_deactivate(self):
        # destroy source
        self.source.do_delete_thyself()
        del self.source


GObject.type_register(ChromecastSource)
