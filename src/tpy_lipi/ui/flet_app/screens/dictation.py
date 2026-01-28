"""Dictation screen for adding journal entries."""

import flet as ft

from tpy_lipi.app import App
from tpy_lipi.ui.flet_app.components.big_button import BigButton


class DictationScreen(ft.Column):
    """Screen for dictating/typing journal entries.

    Features:
    - Text input for entry content (voice input coming later)
    - Topic selector dropdown
    - Save and continue flow
    """

    def __init__(
        self,
        app: App,
        on_navigate: callable | None = None,
        initial_topic: str | None = None,
    ):
        """Create the dictation screen.

        Args:
            app: The application instance with services.
            on_navigate: Callback for navigation (route: str) -> None.
            initial_topic: Pre-selected topic name, if any.
        """
        super().__init__()
        self.app = app
        self.on_navigate = on_navigate
        self._initial_topic = initial_topic
        self.expand = True
        self.spacing = 16
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Header
        self._header = ft.Text(
            "Add Entry",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # Topic selector
        self._topic_dropdown = ft.Dropdown(
            label="Topic",
            hint_text="Select a topic",
            width=300,
            text_size=18,
        )

        # Entry text area
        self._entry_field = ft.TextField(
            label="Your thoughts",
            hint_text="What's on your mind about this topic?",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            text_size=18,
        )

        # Voice button placeholder (for future Whisper integration)
        self._voice_btn = BigButton(
            text="Voice Input",
            icon=ft.Icons.MIC,
            bgcolor=ft.Colors.ORANGE_700,
            width=250,
            on_click=self._on_voice_click,
            disabled=True,  # Disabled until Whisper is integrated
        )
        self._voice_hint = ft.Text(
            "Voice input coming soon",
            size=12,
            color=ft.Colors.GREY_500,
            italic=True,
        )

        # Action buttons
        self._save_btn = BigButton(
            text="Save Entry",
            icon=ft.Icons.SAVE,
            on_click=self._on_save,
            bgcolor=ft.Colors.GREEN_700,
            width=250,
        )
        self._cancel_btn = BigButton(
            text="Cancel",
            icon=ft.Icons.CLOSE,
            on_click=self._on_cancel,
            bgcolor=ft.Colors.GREY_600,
            width=250,
        )

        # Build layout
        self.controls = [
            ft.Container(height=20),
            self._header,
            self._topic_dropdown,
            ft.Container(
                content=self._entry_field,
                padding=ft.padding.symmetric(horizontal=20),
                expand=True,
            ),
            ft.Column(
                controls=[self._voice_btn, self._voice_hint],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            ft.Row(
                controls=[self._cancel_btn, self._save_btn],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Container(height=20),
        ]

    def did_mount(self):
        """Called when the screen is mounted. Load data."""
        self._load_topics()

    def _load_topics(self):
        """Load topics for the dropdown."""
        today = self.app.journal.get_today()
        topics = today.topic_mentions

        # If no topics mentioned today, show recent topics
        if not topics:
            recent = self.app.topics.list_recent_topics(days=14)
            topics = [t.name for t in recent]

        self._topic_dropdown.options = [ft.dropdown.Option(key=name, text=name) for name in topics]

        # Set initial topic if provided
        if self._initial_topic and self._initial_topic in topics:
            self._topic_dropdown.value = self._initial_topic
        elif topics:
            self._topic_dropdown.value = topics[0]

        if self.page:
            self.update()

    def _on_voice_click(self, e):
        """Handle voice button click (placeholder)."""
        # TODO: Integrate Whisper STT
        pass

    def _on_save(self, e):
        """Save the entry and return to home."""
        topic_name = self._topic_dropdown.value
        content = self._entry_field.value.strip()

        if not topic_name:
            self._show_error("Please select a topic")
            return

        if not content:
            self._show_error("Please enter some content")
            return

        # Save the entry
        self.app.journal.add_entry(topic_name, content)

        if self.on_navigate:
            self.on_navigate("home")

    def _on_cancel(self, e):
        """Cancel and return to home."""
        if self.on_navigate:
            self.on_navigate("home")

    def _show_error(self, message: str):
        """Show an error snackbar."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.RED_700,
            )
            self.page.snack_bar.open = True
            self.page.update()
