import rb
from gi.repository import GObject, Gio, GLib, Peas, Gtk, PeasGtk
from gi.repository import RB

class PleerConfig(GObject.Object, PeasGtk.Configurable):
	_gtype_name_ = 'PleerConfig'
	object = GObject.property(type=GObject.Object)
	
	def do_create_configure_widget(self):
		schema_src = Gio.SettingsSchemaSource.new_from_directory(self.plugin_info.get_module_dir(), Gio.SettingsSchemaSource.get_default(), False)
		schema = schema_src.lookup('org.gnome.rhythmbox.plugins.pleer', False)
		self.settings = Gio.Settings.new_full(schema, None, None)
		
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.plugin_info.get_module_dir() + '/ui/pleer-prefs.ui')
		
		self.config = self.builder.get_object('pleer-prefs')
		
		self.dir_dl = self.builder.get_object('dir_download_string')
		self.dir_bt = self.builder.get_object('dir_download_bt')
		
		self.dir_dl.connect('changed', self.on_dirDownloadString_changed)
		self.settings.bind('dir-download-string', self.dir_dl, 'text', Gio.SettingsBindFlags.GET)
		
		self.dir_bt.connect('clicked', self.on_dirDownloadBt_clicked)
		
		content = self.builder.get_object('pleer-prefs')

		return content
	
	def on_dirDownloadString_changed(self, widget):
		self.settings.set_string('dir-download-string', self.dir_dl.get_text())
		
	def on_dirDownloadBt_clicked(self, widget):
		
		def response_handler(widget, response):
			if response == Gtk.ResponseType.OK:
				self.dir_dl.set_text(self.chooser.get_filename())
			self.chooser.destroy()
		
		self.chooser = Gtk.FileChooserDialog(
			title='Choose downloads directory', 
			parent=None, 
			action=Gtk.FileChooserAction.SELECT_FOLDER, 
			buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		
		self.chooser.connect('response', response_handler)
		self.chooser.set_modal(True)
		self.chooser.set_transient_for(self.config.get_toplevel())
		self.chooser.present()
	

GObject.type_register(PleerConfig)