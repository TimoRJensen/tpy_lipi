# tpy_lipi

A Python app for daily reflections: capture thoughts via voice, manage recurring topics, and export Obsidian-compatible markdown – fully offline.

## Features

- **Voice-first journaling**: Dictate your daily reflections using offline speech-to-text (Whisper)
- **Topic management**: Track recurring topics with fuzzy duplicate detection
- **Obsidian integration**: Export daily notes as markdown with `[[wiki links]]`
- **Offline-first**: All processing happens on-device, no internet required
- **Cross-platform**: Android and Desktop via Flet framework

## Installation

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repository
git clone https://github.com/TimoRJensen/tpy_lipi.git
cd tpy_lipi

# Install with all dependencies
uv sync --extra all

# Or install only what you need
uv sync --extra dev          # Development (pytest, ruff)
uv sync --extra ui           # Flet UI
uv sync --extra speech       # Whisper STT
```

## Usage

```bash
# Run the app
uv run python main.py

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Development

See [plan.md](plan.md) for detailed architecture documentation.

### Architecture

The project uses a hexagonal (ports & adapters) architecture:

- **Core** (`src/tpy_lipi/core/`): UI-agnostic business logic, domain models, and port interfaces
- **Adapters** (`src/tpy_lipi/adapters/`): Implementations for storage, speech, notifications, git sync
- **UI** (`src/tpy_lipi/ui/`): Flet app for Android/Desktop, TUI planned

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/core/test_topic_service.py

# With coverage
uv run pytest --cov=tpy_lipi
```

## License
GPL-3.0 License © 2026 Timo R. Jensen
