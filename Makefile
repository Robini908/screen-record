PREFIX ?= /usr/local
ICON_DIR = $(PREFIX)/share/icons/hicolor/scalable/apps
DESKTOP_DIR = $(PREFIX)/share/applications

install:
	pip install .
	install -Dm644 data/icons/io.github.screencast-recorder.svg \
		$(DESTDIR)$(ICON_DIR)/io.github.screencast-recorder.svg
	install -Dm644 data/io.github.screencast-recorder.desktop \
		$(DESTDIR)$(DESKTOP_DIR)/io.github.screencast-recorder.desktop
	gtk-update-icon-cache -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/ || true

uninstall:
	pip uninstall -y screencast-recorder
	rm -f $(DESTDIR)$(ICON_DIR)/io.github.screencast-recorder.svg
	rm -f $(DESTDIR)$(DESKTOP_DIR)/io.github.screencast-recorder.desktop
	gtk-update-icon-cache -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/ || true

.PHONY: install uninstall
