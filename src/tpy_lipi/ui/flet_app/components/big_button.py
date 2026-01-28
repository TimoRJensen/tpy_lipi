"""Car-friendly large button component."""

import flet as ft


class BigButton(ft.ElevatedButton):
    """A large, easy-to-tap button designed for car use.

    Features:
    - Large touch target (minimum 80px height)
    - Large text for readability
    - High contrast colors
    """

    def __init__(
        self,
        text: str,
        on_click: ft.ControlEvent | None = None,
        icon: str | None = None,
        color: str = ft.Colors.WHITE,
        bgcolor: str = ft.Colors.BLUE_700,
        width: int | None = None,
        **kwargs,
    ):
        """Create a car-friendly button.

        Args:
            text: Button label text.
            on_click: Click event handler.
            icon: Optional icon name.
            color: Text/icon color.
            bgcolor: Background color.
            width: Optional fixed width.
            **kwargs: Additional Flet button properties.
        """
        super().__init__(
            text=text,
            on_click=on_click,
            icon=icon,
            color=color,
            bgcolor=bgcolor,
            width=width,
            height=80,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
                padding=ft.padding.all(20),
                shape=ft.RoundedRectangleBorder(radius=16),
            ),
            **kwargs,
        )
