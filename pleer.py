# - encoding: utf8
import rb

from gi.repository import GObject, Gio, Peas, Gtk, GdkPixbuf
from gi.repository import RB

from PleerSource import PleerSource
from PleerConfig import PleerConfig



class PleerEntryType(RB.RhythmDBEntryType):
	def __init__(self):
		RB.RhythmDBEntryType.__init__(self, name='pleer')

	def do_can_sync_metadata(self, entry):
		return True

class Pleer(GObject.Object, Peas.Activatable):
	gtype_name = 'Pleer'
	object = GObject.property(type=GObject.GObject)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		shell = self.object
		db = shell.props.db
		model = RB.RhythmDBQueryModel.new_empty(db)
		entry_type = PleerEntryType()
		db.register_entry_type(entry_type)
		what, width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)
		iconfile = Gio.File.new_for_path(self.plugin_info.get_module_dir()+"/vk-symbolic.svg")
		source_group = RB.DisplayPageGroup.get_by_id("library")

		schema_src = Gio.SettingsSchemaSource.new_from_directory(self.plugin_info.get_module_dir(), Gio.SettingsSchemaSource.get_default(), False)
		schema = schema_src.lookup('org.gnome.rhythmbox.plugins.pleer', False)
		settings = Gio.Settings.new_full(schema, None, None)

		self.source = GObject.new(PleerSource, name=_("Pleer"), shell=shell, query_model=model, plugin=self, entry_type=entry_type, settings=settings ,icon=Gio.FileIcon.new(iconfile))
		shell.append_display_page(self.source, source_group)
		shell.register_entry_type_for_source(self.source, entry_type)
		self.source.initialise()

	def do_deactivate(self):
		self.source.delete_thyself()
		self.source = None

