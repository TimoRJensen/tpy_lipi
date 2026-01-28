"""Home screen - main view showing today's topics."""

from datetime import date

import flet as ft

from tpy_lipi.app import App
from tpy_lipi.ui.flet_app.components.big_button import BigButton
from tpy_lipi.ui.flet_app.components.topic_chip import TopicChip


class HomeScreen(ft.Column):
    """Main screen showing today's daily note and topics.

    Features:
    - Displays current date
    - Shows topics mentioned today
    - Quick access to add topics or entries
    """

    def __init__(self, app: App, on_navigate: callable | None = None):
        """Create the home screen.

        Args:
            app: The application instance with services.
            on_navigate: Callback for navigation (route: str) -> None.
        """
        super().__init__()
        self.app = app
        self.on_navigate = on_navigate
        self.expand = True
        self.spacing = 20
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Header with date
        self._date_text = ft.Text(
            date.today().strftime("%A, %B %d, %Y"),
            size=28,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Topics section
        self._topics_header = ft.Text(
            "Topics Today",
            size=20,
            weight=ft.FontWeight.W_500,
        )
        self._topics_wrap = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
        )
        self._no_topics_text = ft.Text(
            "No topics yet. Tap 'Add Topics' to get started.",
            size=16,
            color=ft.Colors.GREY_600,
            italic=True,
        )

        # Action buttons
        self._add_topics_btn = BigButton(
            text="Add Topics",
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self._on_add_topics,
            width=300,
        )
        self._add_entry_btn = BigButton(
            text="Add Entry",
            icon=ft.Icons.EDIT_NOTE,
            on_click=self._on_add_entry,
            bgcolor=ft.Colors.GREEN_700,
            width=300,
        )

        # Build layout
        self.controls = [
            ft.Container(height=20),
            self._date_text,
            ft.Divider(height=30),
            self._topics_header,
            ft.Container(
                content=self._topics_wrap,
                padding=ft.padding.symmetric(horizontal=20),
            ),
            self._no_topics_text,
            ft.Container(expand=True),  # Spacer
            self._add_topics_btn,
            self._add_entry_btn,
            ft.Container(height=20),
        ]

    def did_mount(self):
        """Called when the screen is mounted. Load data."""
        self._refresh_topics()

    def _refresh_topics(self):
        """Refresh the topics display from the daily note."""
        today = self.app.journal.get_today()

        self._topics_wrap.controls.clear()

        if today.topic_mentions:
            self._no_topics_text.visible = False
            for topic_name in today.topic_mentions:
                chip = TopicChip(
                    label=topic_name,
                    selected=True,
                    on_select=lambda e, name=topic_name: self._on_topic_click(name),
                )
                self._topics_wrap.controls.append(chip)
        else:
            self._no_topics_text.visible = True

        if self.page:
            self.update()

    def _on_add_topics(self, e):
        """Handle add topics button click."""
        if self.on_navigate:
            self.on_navigate("topic_select")

    def _on_add_entry(self, e):
        """Handle add entry button click."""
        if self.on_navigate:
            self.on_navigate("dictation")

    def _on_topic_click(self, topic_name: str):
        """Handle topic chip click - navigate to add entry for this topic."""
        if self.on_navigate:
            self.on_navigate(f"dictation?topic={topic_name}")
