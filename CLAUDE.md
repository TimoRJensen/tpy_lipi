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
- Protocol method signatures (ports)
- Configuration dataclasses with no logic

Everything else requires a test first. When in doubt, write the test.

### Mocking Policy

**Mocking is discouraged.** The hexagonal architecture exists specifically to avoid mocks:

- Use real implementations (e.g., `MarkdownStorage` with `tmp_path` fixture)
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

**Models** (`models.py`): Pydantic domain objects
- `Topic` - name, aliases, last_used, created_at; has `to_markdown()`/`from_markdown()`
- `JournalEntry` - id, topic_name, content, recorded_at
- `DailyNote` - date, topic_mentions, entries; has `to_markdown()`/`from_markdown()`

**Services** (`services/`): Business logic
- `TopicService` - CRUD, fuzzy duplicate detection via rapidfuzz
- `JournalService` - add mentions, add entries, get today's note

**Ports** (`ports/`): Protocol-based interfaces (structural typing, not ABC)
- `StoragePort` - topic and daily note persistence

### Adapters Layer (`src/tpy_lipi/adapters/`)

- `MarkdownStorage` - Obsidian-compatible markdown persistence
  - Topics: `{vault}/topics/{name}.md` with `lipi/topic/{sanitized_name}` tag (nested)
  - Daily notes: `{vault}/{YYYY-MM-DD}.md` with `lipi/daily` tag (nested)

### App Wiring (`src/tpy_lipi/app.py`)

```python
class App:
    def __init__(self, vault_path: Path):
        self.storage = MarkdownStorage(vault_path)
        self.topics = TopicService(self.storage)
        self.journal = JournalService(self.storage, self.topics)
```

### Dependency Flow
```
UI → Services → Ports (Protocol interfaces)
                   ↑
               Adapters (MarkdownStorage)
```

## Storage Format

All data is Obsidian-compatible markdown (no JSON). Uses nested Obsidian tags under `lipi/` prefix.

### Tag Naming

Topics use dynamic nested tags: `lipi/topic/{sanitized_name}`

**Sanitization rules** (see `Topic._tag_name()`):
1. Lowercase the name
2. Replace spaces with underscores
3. Remove all characters except `a-z`, `0-9`, `_`

Examples:
- "Project Alpha" → `lipi/topic/project_alpha`
- "Team Meeting" → `lipi/topic/team_meeting`
- "Q&A Session" → `lipi/topic/qa_session`

Daily notes use static tag: `lipi/daily`

**Topic file** (`topics/Project Alpha.md`):
```markdown
---
tags:
  - lipi/topic/project_alpha
aliases:
  - Alpha
last_used: 2026-01-28T14:30:00
created_at: 2026-01-28T10:00:00
---

# Project Alpha
```

**Daily note** (`2026-01-28.md`):
```markdown
---
tags:
  - lipi/daily
---

# 2026-01-28

## Topics of the Day

- [[Project Alpha]]
- [[Team Meeting]]

## Notes

### [[Project Alpha]]

<!-- entry:uuid-here -->
Made progress on the prototype.

<!-- entry:uuid-here -->
Fixed a critical bug.
```

## Key Technical Decisions

- **Python 3.13+** required
- **Pydantic** for data validation and serialization
- **Protocol** for ports (structural typing, not ABC)
- **rapidfuzz** for fuzzy duplicate detection
- **Direct vault writing** - no separate export step
- **Manual DI** via `App` class

## Current Implementation Status

**Implemented (65 tests passing):**
- Domain models with markdown serialization
- MarkdownStorage adapter
- TopicService with fuzzy duplicate detection
- JournalService for daily notes
- App class for DI wiring

**Not yet implemented:**
- Flet UI
- Whisper STT integration
- Notifications
- Git sync
