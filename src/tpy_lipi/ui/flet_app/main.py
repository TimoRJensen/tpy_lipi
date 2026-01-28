"""Main Flet application entry point."""

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import flet as ft

from tpy_lipi.app import App
from tpy_lipi.ui.flet_app.screens.dictation import DictationScreen
from tpy_lipi.ui.flet_app.screens.home import HomeScreen
from tpy_lipi.ui.flet_app.screens.topic_select import TopicSelectScreen


class LipiApp:
    """Main Flet application for tpy_lipi.

    Manages navigation and screen lifecycle.
    """

    def __init__(self, vault_path: Path):
        """Initialize the app.

        Args:
            vault_path: Path to the Obsidian vault directory.
        """
        self.vault_path = vault_path
        self.app = App(vault_path)
        self.page: ft.Page | None = None
        self._current_screen: ft.Control | None = None

    def run(self):
        """Launch the Flet application."""
        ft.app(target=self._main)

    def _main(self, page: ft.Page):
        """Main Flet entry point.

        Args:
            page: The Flet page instance.
        """
        self.page = page

        # Configure page
        page.title = "Lipi - Daily Journal"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.window.width = 400
        page.window.height = 700

        # Mobile-friendly settings
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

        # Navigate to home
        self._navigate("home")

    def _navigate(self, route: str):
        """Navigate to a screen.

        Args:
            route: The route to navigate to. Supports query params like
                   "dictation?topic=MyTopic".
        """
        if not self.page:
            return

        # Parse route and query params
        parsed = urlparse(route)
        path = parsed.path or route.split("?")[0]
        params = parse_qs(parsed.query)

        # Create the appropriate screen
        if path == "home":
            screen = HomeScreen(self.app, on_navigate=self._navigate)
        elif path == "topic_select":
            screen = TopicSelectScreen(self.app, on_navigate=self._navigate)
        elif path == "dictation":
            initial_topic = params.get("topic", [None])[0]
            screen = DictationScreen(
                self.app,
                on_navigate=self._navigate,
                initial_topic=initial_topic,
            )
        else:
            # Unknown route, go home
            screen = HomeScreen(self.app, on_navigate=self._navigate)

        # Update page
        self._current_screen = screen
        self.page.controls.clear()
        self.page.controls.append(
            ft.Container(
                content=screen,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            )
        )
        self.page.update()

        # Trigger did_mount if available
        if hasattr(screen, "did_mount"):
            screen.did_mount()


def run_app(vault_path: Path | str | None = None):
    """Run the Flet application.

    Args:
        vault_path: Path to the Obsidian vault. Defaults to ./vault in cwd.
    """
    vault_path = Path.cwd() / "vault" if vault_path is None else Path(vault_path)

    # Ensure vault directory exists
    vault_path.mkdir(parents=True, exist_ok=True)

    app = LipiApp(vault_path)
    app.run()


if __name__ == "__main__":
    run_app()
