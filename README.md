# tpy_lipi

A Python app for daily reflections: capture thoughts via voice, manage recurring topics, and write directly to your Obsidian vault – fully offline.

## Current Status

**Core functionality implemented** (65 tests passing):
- Topic management with fuzzy duplicate detection
- Daily journal entries with topic mentions
- Direct writing to Obsidian vault as markdown files
- Full `[[wiki link]]` support between topics and daily notes

**Planned:**
- Flet UI for Android/Desktop
- Whisper speech-to-text integration
- Notifications/reminders

## Features

- **Topic management**: Create and track recurring topics with fuzzy duplicate detection (rapidfuzz)
- **Daily journaling**: Capture topic mentions during the day, add detailed notes in the evening
- **Obsidian-native**: All data stored as markdown with YAML frontmatter and `[[wiki links]]`
- **Offline-first**: All processing happens on-device, no internet required

## Installation

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repository
git clone https://github.com/TimoRJensen/tpy_lipi.git
cd tpy_lipi

# Install dependencies
uv sync --extra dev
```

## Usage

```python
from pathlib import Path
from tpy_lipi.app import App

# Point to your Obsidian vault
app = App(Path("/path/to/obsidian/vault"))

# Create topics
app.topics.create_topic("Project Alpha")
app.topics.create_topic("Team Meeting")

# Add topic mentions during the day
app.journal.add_topic_mention("Project Alpha")

# Add detailed entries in the evening
app.journal.add_entry("Project Alpha", "Made great progress on the prototype.")

# Check for similar topics before creating
duplicates = app.topics.find_duplicates("Projekt Alpha")  # finds "Project Alpha"
```

### File Structure in Vault

```
your-vault/
├── topics/
│   ├── Project Alpha.md      # tagged with lipi/topic/project_alpha
│   └── Team Meeting.md       # tagged with lipi/topic/team_meeting
├── 2026-01-28.md              # daily note, tagged with lipi/daily
└── 2026-01-29.md
```

### Nested Obsidian Tags

All tpy_lipi content uses nested tags under the `lipi/` prefix for easy filtering in Obsidian:

- **Topics**: `lipi/topic/{name}` where name is sanitized (lowercase, spaces → underscores)
- **Daily notes**: `lipi/daily`

Examples: "Project Alpha" → `lipi/topic/project_alpha`, "Team Meeting" → `lipi/topic/team_meeting`

## Development

```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest tests/core/test_topic_service.py -v

# Lint and format
uv run ruff check .
uv run ruff format .
```

### Architecture

Hexagonal (ports & adapters) architecture:

- **Core** (`src/tpy_lipi/core/`): Domain models, services, port interfaces
- **Adapters** (`src/tpy_lipi/adapters/`): MarkdownStorage for Obsidian vault
- **App** (`src/tpy_lipi/app.py`): Dependency injection wiring

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

## License

GPL-3.0 License © 2026 Timo R. Jensen
