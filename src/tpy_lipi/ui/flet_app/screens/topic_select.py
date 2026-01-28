"""Topic selection screen for quick topic capture."""

import flet as ft

from tpy_lipi.app import App
from tpy_lipi.ui.flet_app.components.big_button import BigButton
from tpy_lipi.ui.flet_app.components.topic_chip import TopicChip


class TopicSelectScreen(ft.Column):
    """Screen for selecting and creating topics.

    Features:
    - List of recent topics as selectable chips
    - Add new topic with duplicate detection
    - Quick selection for daily capture
    """

    def __init__(self, app: App, on_navigate: callable | None = None):
        """Create the topic selection screen.

        Args:
            app: The application instance with services.
            on_navigate: Callback for navigation (route: str) -> None.
        """
        super().__init__()
        self.app = app
        self.on_navigate = on_navigate
        self.expand = True
        self.spacing = 16
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self._selected_topics: set[str] = set()

        # Header
        self._header = ft.Text(
            "Select Topics",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # New topic input
        self._new_topic_field = ft.TextField(
            label="New Topic",
            hint_text="Enter a new topic name",
            on_submit=self._on_add_new_topic,
            expand=True,
            text_size=18,
        )
        self._add_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE,
            icon_size=40,
            icon_color=ft.Colors.BLUE_700,
            on_click=self._on_add_new_topic,
        )
        self._new_topic_row = ft.Row(
            controls=[self._new_topic_field, self._add_btn],
            spacing=10,
        )

        # Duplicate warning
        self._duplicate_warning = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Similar topics found:",
                        size=14,
                        color=ft.Colors.ORANGE_700,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(wrap=True, spacing=8, run_spacing=8),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.ORANGE_50,
            padding=ft.padding.all(12),
            border_radius=8,
            visible=False,
        )

        # Recent topics section
        self._recent_header = ft.Text(
            "Recent Topics",
            size=18,
            weight=ft.FontWeight.W_500,
        )
        self._topics_wrap = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
        )

        # Action buttons
        self._done_btn = BigButton(
            text="Done",
            icon=ft.Icons.CHECK,
            on_click=self._on_done,
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
            ft.Container(
                content=self._new_topic_row,
                padding=ft.padding.symmetric(horizontal=20),
            ),
            self._duplicate_warning,
            ft.Divider(height=20),
            self._recent_header,
            ft.Container(
                content=self._topics_wrap,
                padding=ft.padding.symmetric(horizontal=20),
                expand=True,
            ),
            ft.Row(
                controls=[self._cancel_btn, self._done_btn],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Container(height=20),
        ]

    def did_mount(self):
        """Called when the screen is mounted. Load data."""
        self._load_topics()
        # Pre-select topics already mentioned today
        today = self.app.journal.get_today()
        self._selected_topics = set(today.topic_mentions)
        self._refresh_chips()

    def _load_topics(self):
        """Load recent topics from storage."""
        self._recent_topics = self.app.topics.list_recent_topics(days=30)

    def _refresh_chips(self):
        """Refresh the topic chips display."""
        self._topics_wrap.controls.clear()

        for topic in self._recent_topics:
            is_selected = topic.name in self._selected_topics
            chip = TopicChip(
                label=topic.name,
                selected=is_selected,
                on_select=lambda e, name=topic.name: self._on_topic_toggle(e, name),
            )
            self._topics_wrap.controls.append(chip)

        if self.page:
            self.update()

    def _on_topic_toggle(self, e, topic_name: str):
        """Handle topic chip selection toggle."""
        if topic_name in self._selected_topics:
            self._selected_topics.discard(topic_name)
        else:
            self._selected_topics.add(topic_name)
        self._refresh_chips()

    def _on_add_new_topic(self, e):
        """Handle adding a new topic."""
        name = self._new_topic_field.value.strip()
        if not name:
            return

        # Check for duplicates
        duplicates = self.app.topics.find_duplicates(name, threshold=80)

        if duplicates:
            # Show duplicate warning
            dup_row = self._duplicate_warning.content.controls[1]
            dup_row.controls.clear()
            for dup in duplicates:
                chip = TopicChip(
                    label=dup.name,
                    on_select=lambda e, n=dup.name: self._use_existing_topic(n),
                )
                dup_row.controls.append(chip)

            # Add "Create anyway" button
            create_anyway = ft.TextButton(
                text="Create anyway",
                on_click=lambda e: self._create_topic(name),
            )
            dup_row.controls.append(create_anyway)

            self._duplicate_warning.visible = True
            if self.page:
                self.update()
        else:
            self._create_topic(name)

    def _create_topic(self, name: str):
        """Create a new topic and select it."""
        self.app.topics.create_topic(name)
        self._selected_topics.add(name)
        self._new_topic_field.value = ""
        self._duplicate_warning.visible = False
        self._load_topics()
        self._refresh_chips()

    def _use_existing_topic(self, name: str):
        """Use an existing topic instead of creating a new one."""
        self._selected_topics.add(name)
        self._new_topic_field.value = ""
        self._duplicate_warning.visible = False
        self._refresh_chips()

    def _on_done(self, e):
        """Save selected topics and return to home."""
        # Add all selected topics to today's mentions
        for topic_name in self._selected_topics:
            self.app.journal.add_topic_mention(topic_name)

        if self.on_navigate:
            self.on_navigate("home")

    def _on_cancel(self, e):
        """Cancel and return to home without saving."""
        if self.on_navigate:
            self.on_navigate("home")
