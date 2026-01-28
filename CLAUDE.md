# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL: TDD is Mandatory

**Test-Driven Development is non-negotiable in this project.** Follow red-green-refactor strictly:

1. **RED**: Write a failing test first
2. **GREEN**: Write the minimum code to make it pass
3. **REFACTOR**: Clean up while keeping tests green

### What This Means in Practice

- **Never write implementation code without a failing test first**
- Write the test, run it, see it fail, then implement
- Commit tests and implementation together or tests first

### Exceptions (Absolute Boilerplate Only)

These do NOT require tests first:
- `__init__.py` files
- Import statements
- Pydantic model field definitions (but test validation logic)
- Abstract base class method signatures (ports)
- Configuration dataclasses with no logic

Everything else requires a test first. When in doubt, write the test.

### Mocking Policy

**Mocking is discouraged.** The hexagonal architecture exists specifically to avoid mocks:

- Use real implementations (e.g., JsonFileStorage with temp directories)
- Use simple in-memory implementations for ports when needed
- Prefer integration tests over unit tests with mocks

**If you believe mocking is necessary:**
1. Stop and explain why
2. Wait for explicit permission before using any mock

Do not use `unittest.mock`, `pytest-mock`, or any mocking library without approval.

## Development Commands

```bash
# Run tests (do this constantly)
uv run pytest

# Run specific test
uv run pytest tests/core/test_topic_service.py::test_name -v

# Run with output
uv run pytest -s

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run the app
uv run python main.py
```

## Architecture

Hexagonal (Ports & Adapters) with three layers:

### Core Layer (`src/tpy_lipi/core/`)
- **Models** (`models.py`): Pydantic domain objects - `Topic`, `JournalEntry`, `DailyNote`
- **Services** (`services/`): Business logic - `TopicService`, `JournalService`, `ExportService`
- **Ports** (`ports/`): Abstract interfaces - `StoragePort`, `SpeechToTextPort`, etc.

### Adapters Layer (`src/tpy_lipi/adapters/`)
Concrete implementations:
- `JsonFileStorage` - File-based persistence
- `WhisperSpeechToText` - Offline STT via faster-whisper
- Notification adapters (Android, Desktop)

### UI Layer (`src/tpy_lipi/ui/`)
- `flet_app/` - Flet framework (Android/Desktop)
- `tui/` - Terminal UI (planned)

### Dependency Flow
```
UI → Services → Ports (interfaces)
                   ↑
               Adapters
```

Wiring happens in `main.py` via manual dependency injection.

## Key Technical Decisions

- **Python 3.13+** required
- **Pydantic** for data validation
- **rapidfuzz** for fuzzy duplicate detection
- **faster-whisper** for offline speech-to-text
- **Manual DI** - no framework needed

## Data Directories (gitignored)

- `data/` - User data (topics, journal entries, exports)
- `models/` - Whisper speech recognition models
