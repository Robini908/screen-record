import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


class RegionSelector(Gtk.Window):
    def __init__(self, parent_window):
        super().__init__(title="Select Region", transient_for=parent_window,
                         modal=True, decorated=False)

        from .display import get_monitors
        monitors = get_monitors()
        if monitors:
            _, sw, sh, sx, sy = monitors[0]
            self.set_default_size(min(sw, 1400), min(sh, 900))
        else:
            self.set_default_size(800, 600)

        self.parent = parent_window
        self.start_x = self.start_y = -1
        self.current_x = self.current_y = 0
        self.selection = None

        self.overlay = Gtk.Overlay()
        self.set_child(self.overlay)

        self.da = Gtk.DrawingArea()
        self.da.set_vexpand(True)
        self.da.set_hexpand(True)
        self.da.set_draw_func(self._draw, None)
        self.overlay.set_child(self.da)

        css = b"""
        .region-selector { background: rgba(0,0,0,0.3); }
        .region-info { background: white; padding: 8px; border-radius: 8px; }
        """
        prov = Gtk.CssProvider()
        prov.load_from_bytes(GLib.Bytes.new(css))
        self.get_style_context().add_provider(prov, 1)

        evk = Gtk.EventControllerKey()
        evk.connect("key-pressed", self._on_key)
        self.add_controller(evk)

        self.click = Gtk.GestureClick()
        self.click.connect("pressed", self._on_press)
        self.click.connect("released", self._on_release)
        self.click.connect("motion", self._on_motion)
        self.da.add_controller(self.click)

        self.motion = Gtk.EventControllerMotion()
        self.motion.connect("motion", self._on_motion_hover)
        self.da.add_controller(self.motion)

        self.connect("close-request", self._on_close)

    def _on_key(self, ctrl, keyval, keycode, state):
        if keyval == 65307:
            self.close()
        return True

    def _on_press(self, gesture, n_press, x, y):
        self.start_x = int(x)
        self.start_y = int(y)

    def _on_motion(self, gesture, x, y):
        self.current_x = int(x)
        self.current_y = int(y)
        self.da.queue_draw()

    def _on_motion_hover(self, ctrl, x, y):
        pass

    def _on_release(self, gesture, n_press, x, y):
        if self.start_x < 0:
            return
        x1 = min(self.start_x, int(x))
        y1 = min(self.start_y, int(y))
        x2 = max(self.start_x, int(x))
        y2 = max(self.start_y, int(y))
        rx, ry, rw, rh = x1, y1, x2 - x1, y2 - y1
        if rw < 10 or rh < 10:
            return
        self.parent.config["geometry"] = f"{rx} {ry} {rw} {rh}"
        self.parent.config["mode"] = "region"
        self.close()

    def _on_close(self, *a):
        return False

    def _draw(self, da, cr, w, h, data):
        cr.set_source_rgba(0, 0, 0, 0.3)
        cr.paint()
        if self.start_x >= 0:
            cr.set_source_rgba(1, 0.3, 0.3, 0.3)
            cr.rectangle(
                self.start_x, self.start_y,
                self.current_x - self.start_x,
                self.current_y - self.start_y,
            )
            cr.fill()
            cr.set_source_rgb(1, 0, 0)
            cr.set_line_width(2)
            cr.rectangle(
                self.start_x, self.start_y,
                self.current_x - self.start_x,
                self.current_y - self.start_y,
            )
            cr.stroke()
