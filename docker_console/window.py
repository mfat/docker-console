"""Main application window: a tabbed shell hosting the Docker Console page plus
any interactive terminal tabs, with a toast overlay for notifications."""

from __future__ import annotations

from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa: E402

from .connections import LOCAL_NICKNAME, ConnectionRegistry
from .context import AppContext
from .page import DockerConsolePage
from .settings import Settings


class DockerConsoleWindow(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application,
                 registry: Optional[ConnectionRegistry] = None,
                 settings: Optional[Settings] = None) -> None:
        super().__init__(application=application)
        self.set_title("Docker Console")
        self.set_default_size(1000, 680)

        self._registry = registry or ConnectionRegistry()
        self._settings = settings or Settings()
        self.ctx = AppContext(self._registry, self._settings, window=self)

        self._tab_view = Adw.TabView()
        tab_bar = Adw.TabBar(view=self._tab_view)

        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title="Docker Console", subtitle=""))

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.add_top_bar(tab_bar)

        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(self._tab_view)
        toolbar.set_content(self._toast_overlay)
        self.set_content(toolbar)

        # Don't close the main page tab via the terminal-tab close machinery.
        self._tab_view.connect("close-page", self._on_close_page)

        page = DockerConsolePage(self.ctx, initial_host=LOCAL_NICKNAME)
        self._page_tab = self._tab_view.append(page)
        self._page_tab.set_title("Docker Console")
        self._tab_view.set_page_pinned(self._page_tab, True)

    # -- terminal tabs ----------------------------------------------------
    def add_terminal_tab(self, widget: Gtk.Widget, title: str) -> Adw.TabPage:
        page = self._tab_view.append(widget)
        page.set_title(title)
        self._tab_view.set_selected_page(page)
        return page

    def _on_close_page(self, view: Adw.TabView, page: Adw.TabPage) -> bool:
        # Terminal tabs close normally; the pinned main page can't be closed.
        view.close_page_finish(page, page is not self._page_tab)
        return True  # we handled it

    # -- notifications ----------------------------------------------------
    def toast(self, message: str) -> None:
        self._toast_overlay.add_toast(Adw.Toast.new(message))
