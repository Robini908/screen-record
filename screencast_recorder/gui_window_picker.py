import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class WindowPicker(Gtk.Window):
    def __init__(self, parent_window):
        super().__init__(title="Select Window", transient_for=parent_window,
                         modal=True)
        self.parent = parent_window
        self.set_default_size(500, 400)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search windows…")
        self.search_entry.connect("search-changed", self._on_search)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self._on_activated)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.listbox)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: self.close())

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.append(cancel_btn)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_margin(12)
        outer.append(self.search_entry)
        outer.append(scrolled)
        outer.append(btn_box)

        self.set_child(outer)
        self._windows = []
        self._populate()

    def _populate(self):
        from .windows import list_windows
        self._windows = list_windows()
        for w in self._windows:
            self.listbox.append(
                Gtk.Label(label=f"{w['name']} ({w['w']}x{w['h']})",
                          xalign=0)
            )

    def _on_search(self, entry):
        query = entry.get_text().lower()
        for i, w in enumerate(self._windows):
            row = self.listbox.get_row_at_index(i)
            if row:
                row.set_visible(query in w["name"].lower())

    def _on_activated(self, lb, row):
        idx = row.get_index()
        if idx < len(self._windows):
            w = self._windows[idx]
            self.parent.config["geometry"] = f"{w['x']} {w['y']} {w['w']} {w['h']}"
            self.parent.config["mode"] = "window"
        self.close()
