import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, Adw


class RecordApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.screencast-recorder",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        from .gui_window import RecordWindow
        win = RecordWindow(application=self)
        win.connect("close-request", win._on_close_request)
        win.present()


def gui_main():
    app = RecordApp()
    app.run(None)
