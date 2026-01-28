"""Entry point for tpy_lipi application."""

import sys
from pathlib import Path

from tpy_lipi import __version__


def main() -> None:
    """Launch the tpy_lipi application."""
    # Parse optional vault path from command line
    vault_path = None
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])

    print(f"tpy_lipi v{__version__}")

    # Import here to avoid loading Flet for --version checks
    from tpy_lipi.ui.flet_app.main import run_app

    run_app(vault_path)


if __name__ == "__main__":
    main()
