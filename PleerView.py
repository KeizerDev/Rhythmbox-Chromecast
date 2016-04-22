# - encoding: utf8
import rb

from gi.repository import GObject, Gio, Peas, Gtk, GdkPixbuf
from gi.repository import RB

class PleerView(RB.EntryView):
	def initialise(self, source):
		self.source = source
		self.plugin = self.source.props.plugin
		
		# Prepare context menu (right-click track)
		ui = Gtk.Builder()
		ui.add_from_file(self.plugin.plugin_info.get_module_dir() + '/ui/pleer_entryview.xml')
		ui.connect_signals(self.source)
		self.popup_menu = ui.get_object('entryview_popup_menu')
		
		self.append_column(RB.EntryViewColumn.TITLE, True)
		self.append_column(RB.EntryViewColumn.ARTIST, True)
		self.append_column(RB.EntryViewColumn.DURATION, True)
		self.append_column(RB.EntryViewColumn.QUALITY, True)
		self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
	
	# Called when a row (track) is double-ckicked
	def do_entry_activated(self, entry):
		if self.get_selected_entries()[0]:
			self.props.shell_player.stop() # Prevents RB from crashing (>search, >play, >search same thing, >play other song)
			self.props.shell_player.play_entry(self.get_selected_entries()[0], self.source)
	
	# Called when a row (track) is right-clicked
	def do_show_popup(self, over_entry):
		if over_entry:
			self.popup_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
		
		return over_entry

