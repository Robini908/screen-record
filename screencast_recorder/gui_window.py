import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from .helpers import load_config, save_config, is_recording
from .gui_settings import build_settings_page
from .gui_recording import build_recording_page, RecordingController


class RecordWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = RecordingController()

        self.config = load_config()
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.recording_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._build_ui()
        self._setup_shortcuts()
        self._apply_css()

        if is_recording():
            from .gui_recording import build_recording_page
            build_recording_page(self)
            GLib.timeout_add(500, self.controller.tick, self)
        else:
            self.stack.set_visible_child(self.settings_box)
            build_settings_page(self)

    def _build_ui(self):
        self.stack.add_named(self.settings_box, "settings")
        self.stack.add_named(self.recording_box, "recording")
        self.set_content(self.stack)
        self.set_default_size(480, 620)
        self.set_resizable(False)
        self.stack.set_visible_child(self.settings_box)

    def _setup_shortcuts(self):
        ctrl = Gtk.EventControllerKey()
        ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(ctrl)

    def _on_key_pressed(self, ctrl, keyval, keycode, state):
        if keyval == 65307:
            self.close()
            return True
        return False

    def _apply_css(self):
        css = b"""
        .section { margin: 8px 0; }
        .section-title { font-weight: bold; margin: 4px 0; }
        .recording-label { font-size: 48px; font-weight: bold; }
        .paused-label { font-size: 36px; color: #e66100; }
        """
        prov = Gtk.CssProvider()
        prov.load_from_bytes(css)
        self.get_style_context().add_provider(prov, 1)

    def _navigate_to(self, page_name):
        self.stack.set_visible_child(self.settings_box if page_name == "settings"
                                     else self.recording_box)

    def _set_status(self, msg, timeout=3000):
        if hasattr(self, "toast"):
            self.toast.dismiss()
        self.toast = Adw.Toast(title=msg, timeout=timeout)
        if hasattr(self, "toast_overlay"):
            self.toast_overlay.add_toast(self.toast)

    def _on_start(self):
        self._navigate_to("recording")
        from .helpers import clear_status
        clear_status()
        self.controller.start(self)

    def _on_pause(self):
        self.controller.toggle_pause(self)

    def _on_stop(self):
        self.controller.stop(self)

    def _on_close_request(self, *args):
        self._save_config()
        return False

    def _save_config(self):
        save_config(self.config)
