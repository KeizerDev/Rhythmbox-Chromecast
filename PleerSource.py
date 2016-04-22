from gi.repository import GObject, Gio, GLib, Peas, Gtk, Gdk
from gi.repository import RB

import threading
import os

from PleerSearch import PleerSearch
from PleerView import PleerView
from PleerConfig import PleerConfig

import urllib.request

class PleerSource(RB.Source):
	def __init__(self, **kwargs):
		super(PleerSource, self).__init__(kwargs)
		self.initialised = False
	
	def initialise(self):
		shell = self.props.shell
		
		self.entry_view = PleerView(db=shell.props.db, shell_player=shell.props.shell_player, is_drag_source=True, is_drag_dest=False)
		self.entry_view.initialise(source=self)
		
		self.downloading = False
		
		self.search_entry = Gtk.SearchEntry()
		self.search_entry.set_width_chars(100)
		self.search_entry.set_activates_default(True)
		
		self.dl_progress_bar = Gtk.ProgressBar()
		self.dl_progress_bar.set_show_text(True)
		self.dl_progress_bar.set_opacity(0)
		
		self.search_button = Gtk.Button("Search")
		self.search_button.connect("clicked", self.on_search_button_clicked)
		self.search_button.set_can_default(True)
		
		self.loadMore_button = Gtk.Button('Load more')
		self.loadMore_button.connect('clicked', self.on_loadMore_button_clicked)
		self.loadMore_button.set_sensitive(False)
		
		hbox = Gtk.HBox()
		hbox.pack_start(self.search_entry, False, False, 0)
		hbox.pack_start(self.search_button, False, False, 5)
		hbox.pack_start(self.loadMore_button, False, False, 5)
		hbox.pack_start(self.dl_progress_bar, False, False, 5)
		
		vbox = Gtk.VBox()
		vbox.pack_start(hbox, False, False, 0)
		vbox.pack_start(self.entry_view, True, True, 5)
		
		self.pack_start(vbox, True, True, 0)
		self.show_all()
		#shell.get_ui_manager().ensure_update()
		self.initialised = True


	def do_impl_get_entry_view(self):
		return self.entry_view

	# rhyhtmbox api break up (0.13.2 - 0.13.3)
	def do_impl_activate(self):
		self.do_selected()

	def do_selected(self):
		if not self.initialised:
			self.initialise()
		self.search_button.grab_default()

	# rhyhtmbox api break up (0.13.2 - 0.13.3)
	def do_impl_get_status(self):
		return self.do_get_status()

	def do_get_status(self, status, progress_text, progress):
		status = 'Pleer: '
		if hasattr(self, 'downloading') and self.downloading:
			status += 'Downloading 1 file : '+ self.downloading_filename +' in '+ self.downloading_directory
		elif hasattr(self, 'search') and isinstance(self.search, PleerSearch):
			if self.search.is_complete():
				status += self.search.search_term +' : '+ str(self.search.search_total) +' tracks found'
			else:
				status += 'Searching '+ self.search.search_term +'...'
		elif hasattr(self, 'error_msg'):
			status += self.error_msg
		else:
			status = 'Pleer'
		
		return (status, "xyz", 1)

	def do_impl_delete_thyself(self):
		if self.initialised:
			self.props.shell.props.db.entry_delete_by_type(self.props.entry_type)
		RB.Source.do_impl_delete_thyself(self)

	def do_impl_can_add_to_queue(self):
		return True

	def do_impl_can_pause(self):
		return True
	
	def on_search_button_clicked(self, button):
		entry = self.search_entry
		if entry.get_text():
			self.search = PleerSearch(entry.get_text(), self.props.shell.props.db, self.props.entry_type)
			
			self.loadMore_button.set_sensitive(True)
			# Start the search asynchronously
			GLib.idle_add(self.search.start, priority=GLib.PRIORITY_HIGH_IDLE)
			
			self.props.query_model = self.search.query_model
			self.entry_view.set_model(self.props.query_model)

	def on_loadMore_button_clicked(self, button):
		self.search.loadMore()
	
	# Handler for Download MenuItem (See PleerView)
	def download_song(self, menuItem):
		self.downloading_directory = self.props.settings.get_string('dir-download-string')
		if self.downloading_directory.endswith('/'):
			self.downloading_directory = self.downloading_directory[:-1]
		
		if os.path.isdir(self.downloading_directory):
			selectedEntry = self.entry_view.get_selected_entries()[0]
			songArtist = selectedEntry.get_string(RB.RhythmDBPropType.ARTIST)
			songTitle = selectedEntry.get_string(RB.RhythmDBPropType.TITLE)
			self.downloading_filename = songArtist +' - '+ songTitle +' (Pleer).mp3'
			self.downloading_uri = selectedEntry.get_playback_uri()
			
			thread = threading.Thread(target=self.th_download_song)
			thread.daemon = True
			thread.start()
		else:
			self.error_msg = 'Please provide a valid directory for downloads. Current directory is "'+ self.downloading_directory +'". '
			self.error_msg += '(Check Pleer plugin preferences.)'
			self.notify_status_changed()
	
	# Threading song download to avoid Rhythmbox being blocked
	def th_download_song(self):
		self.downloading = True
		self.notify_status_changed()
		self.dl_progress_bar.set_opacity(1)
		urllib.request.urlretrieve(self.downloading_uri, self.downloading_directory +'/'+ self.downloading_filename, self.cb_download_song)
		self.downloading = False
		self.dl_progress_bar.set_opacity(0)
		self.notify_status_changed()
	
	def cb_download_song(self, transferedBlocks, blockSize, fileSize):
		received = transferedBlocks * blockSize
		if received != 0:
			self.dl_progress_bar.set_fraction(received / fileSize)
	
	# TODO:This function causes a Gtk-CRITICAL error when exiting Rhythmbox.
	# Handler for Copy URI MenuItem (See PleerView)
	def copy2clipboard(self, menuItem):
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clipboard.set_text(self.entry_view.get_selected_entries()[0].get_playback_uri(), -1)
		
		

GObject.type_register(PleerSource)
