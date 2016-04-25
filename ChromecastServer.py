import json
import os
import re
import time
import cgi
import os
import sys
import time
import socket
from urllib.parse import urlparse, unquote
from wsgiref.simple_server import make_server
import io
import os, errno

from gi.repository import RB, GObject, Gtk, Gio

PYVER = sys.version_info[0]
if PYVER >= 3:
    import io


class ChromecastServer(object):
    def __init__(self, hostname, port, plugin):
        self.plugin = plugin
        self.running = True
        self.artist = None
        self.album = None
        self.title = None
        self.stream = None
        self.initial_playlist_rows = None
        self._httpd = make_server(hostname, port, self._wsgi)
        self._watch_cb_id = GObject.io_add_watch(self._httpd.socket,
                                                 GObject.IO_IN,
                                                 self._idle_cb)
        self._cover_db = RB.ExtDB(name='album-art')

    def shutdown(self):
        GObject.source_remove(self._watch_cb_id)
        self.running = False
        self.plugin = None

    def set_playing(self, artist, album, title, stream, uri):
        self.artist = artist
        self.album = album
        self.title = title
        self.stream = stream
        self.uri = uri

    def _idle_cb(self, source, cb_condition):
        if not self.running:
            return False
        self._httpd.handle_request()
        return True

    def _wsgi(self, environ, response):
        path = environ['PATH_INFO']

        log("wsgi", path)
        if path in ('/', ''):
            log("current", response)
            return self._handle_current(response)

    def _handle_current(self, response):
        shell = self.plugin.get_property("shell")
        player = shell.get_property("shell-player")
        db = self.plugin.db

        song = ""

        if player.get_playing_entry() is not None:
            # something is playing; get the track list from the play queue or the current playlists
            fname = urlparse(player.get_playing_entry().get_playback_uri())
            filename = unquote(fname.path).encode('utf8')
            symlink_force(filename, resolve_path('play.mp3'))
        else:
            song = ""
        # handle any action
        #
        # title = 'Rhythmweb'
        # playing = '<span id="not-playing">%s</span>' % song

        # player_html = open(resolve_path('play.mp3'))

        # result = player_html.read() % {'title': title,
        #                                'playing': playing}
        #
        # player_html.close()



        if PYVER >= 3:
            track = open(resolve_path('play.mp3'), "rb")
        else:
            track = open(resolve_path('play.mp3'))

        lastmod = time.gmtime(os.path.getmtime(resolve_path('play.mp3')))
        lastmod = time.strftime("%a, %d %b %Y %H:%M:%S +0000", lastmod)
        response_headers = [('Content-type', "audio/mpeg"),
                            ('Last-Modified', lastmod)]
        response('200 OK', response_headers)
        if PYVER >= 3:
            result = io.BytesIO(track.read())
        else:
            result = track.read()

        return result


def parse_post(environ):
    if 'CONTENT_TYPE' in environ:
        length = -1
        if 'CONTENT_LENGTH' in environ:
            contLength = environ['CONTENT_LENGTH']
            if contLength:
                length = int(contLength)
        if environ['CONTENT_TYPE'].startswith('application/x-www-form-urlencoded'):
            return cgi.parse_qs(environ['wsgi.input'].read(length))
        if environ['CONTENT_TYPE'].startswith('multipart/form-data'):
            return cgi.parse_multipart(environ['wsgi.input'].read(length))
    return None


def resolve_path(path):
    return os.path.join(os.path.dirname(__file__), path)


def log(message, args):
    # when debugging incomment the following line
    # sys.stdout.write("log %s:[%s]\n" % (message, args))
    return


def bytestring(string):
    log("bytestring", string)
    if PYVER >= 3:
        return string.encode()
    else:
        return string


def iostring(bytestr):
    log("iostring", bytestr)
    if PYVER >= 3:
        return io.BytesIO(bytestring(bytestr))
    else:
        return bytestr


def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def resolve_path(path):
    return os.path.join(os.path.dirname(__file__), path)
