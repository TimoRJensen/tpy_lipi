"""Topic chip component for displaying and selecting topics."""

import flet as ft


class TopicChip(ft.Chip):
    """A chip for displaying a topic that can be selected/deselected.

    Features:
    - Large touch target for car use
    - Visual feedback for selected state
    - Delete action for removing from selection
    """

    def __init__(
        self,
        label: str,
        selected: bool = False,
        on_select: ft.ControlEvent | None = None,
        on_delete: ft.ControlEvent | None = None,
        **kwargs,
    ):
        """Create a topic chip.

        Args:
            label: Topic name to display.
            selected: Whether the chip is currently selected.
            on_select: Handler called when chip is clicked.
            on_delete: Handler called when delete icon is clicked (optional).
            **kwargs: Additional Flet chip properties.
        """
        super().__init__(
            label=ft.Text(label, size=18),
            selected=selected,
            on_select=on_select,
            on_delete=on_delete,
            delete_icon_color=ft.Colors.RED_400 if on_delete else None,
            selected_color=ft.Colors.BLUE_100,
            bgcolor=ft.Colors.GREY_200,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            label_padding=ft.padding.only(right=8),
            **kwargs,
        )
