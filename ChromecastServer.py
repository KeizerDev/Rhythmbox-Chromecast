import os
import sys
import time
from wsgiref.simple_server import make_server

from gi.repository import GObject

from Utils import resolve_path

PYVER = sys.version_info[0]
if PYVER >= 3:
    import io


class ChromecastServer(object):
    def __init__(self, hostname, port, plugin):
        self.plugin = plugin
        self.running = True
        self._httpd = make_server(hostname, port, self._wsgi)
        self._watch_cb_id = GObject.io_add_watch(self._httpd.socket,
                                                 GObject.IO_IN,
                                                 self._idle_cb)

    def shutdown(self):
        GObject.source_remove(self._watch_cb_id)
        self.running = False
        self.plugin = None

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
