# Obsidian Daybook Assistant

> A Python app (Flet framework) that supports daily journaling in Obsidian – with voice input, topic management, and an offline-first approach.

---

## 1. Project Goal

An app that:
- Reminds about daily notes regularly (quiet during the day, prominent in the evening)
- Processes voice input (speech-to-text) offline on-device
- Maintains a topic catalog and detects duplicates
- Generates Obsidian-compatible Markdown files with `[[wiki links]]`
- Optionally syncs with Git
- Is written entirely in Python (Flet framework)
- Has a clean separation of core and UI (for future TUI/CLI support)

---

## 2. Core Features

| Area              | Feature                                               | Priority         |
| ----------------- | ----------------------------------------------------- | ---------------- |
| **Reminders**     | Silent push notifications during the day (quick topic capture) | High          |
|                   | Evening notification for detailed reflection          | High             |
| **Speech**        | Speech-to-text for dictation (offline, on-device)     | High             |
|                   | Text-to-speech for instructions (car mode)            | Medium           |
|                   | Voice control for navigation                          | Low (later)      |
| **Topic Catalog** | List of active topics from recent days/weeks          | High             |
|                   | Duplicate detection for new topics (fuzzy matching)   | Medium           |
|                   | Hierarchy (parent/child topics)                       | Deferred         |
| **Output**        | Obsidian Markdown with `[[Links]]`                    | High             |
|                   | Local `.md` files                                     | High             |
|                   | Git sync (manual trigger)                             | Medium           |

---

## 3. Interaction Flow

### During the Day (multiple times, silent notification)

```
→ Open app
→ Quick selection: Which topics came up?
→ Optional: Add new topic (with duplicate check)
→ Done (< 30 seconds)
```

### Evening (once, prominent notification)

```
→ App shows collected topics of the day
→ Per topic: Voice input for details
→ Next button / Next topic
→ Export as Daily Note
```

---

## 4. Architecture (Hexagonal / Ports & Adapters)

### Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (swappable)                     │
├─────────────────────────────────────────────────────────────┤
│  • Flet (Android/Desktop)                                   │
│  • TUI (Textual / Rich)                                     │
│  • CLI (Click/Typer)                                        │
│  • Later: Web?                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses only interfaces
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Layer (UI-agnostic)                  │
├─────────────────────────────────────────────────────────────┤
│  Services                                                   │
│  • TopicService (CRUD, duplicate checking)                  │
│  • JournalService (manage daily entries)                    │
│  • ReminderService (scheduling logic) [not yet implemented] │
├─────────────────────────────────────────────────────────────┤
│  Domain Models                                              │
│  • Topic(name, parent?, last_used, aliases)                 │
│  • JournalEntry(date, topic, content)                       │
│  • DailyNote(date, entries[])                               │
├─────────────────────────────────────────────────────────────┤
│  Ports (Abstract Interfaces)                                │
│  • SpeechToTextPort                                         │
│  • TextToSpeechPort                                         │
│  • StoragePort                                              │
│  • NotificationPort                                         │
│  • GitSyncPort                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ Dependency Injection
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Adapters (Implementations)                  │
├─────────────────────────────────────────────────────────────┤
│  • MarkdownStorage(StoragePort) ✓ IMPLEMENTED               │
│  • WhisperSpeechToText(SpeechToTextPort)                    │
│  • AndroidTTS(TextToSpeechPort)                             │
│  • AndroidNotification(NotificationPort)                    │
│  • DesktopNotification(NotificationPort)                    │
│  • GitPythonSync(GitSyncPort)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Project Structure

```
tpy_lipi/
├── src/
│   └── tpy_lipi/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py                 # Topic, JournalEntry, DailyNote (Pydantic)
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── topic_service.py      # CRUD, duplicate checking ✓
│       │   │   └── journal_service.py    # Manage daily entries ✓
│       │   └── ports/
│       │       ├── __init__.py
│       │       ├── speech.py             # SpeechToTextPort, TextToSpeechPort
│       │       ├── storage.py            # StoragePort
│       │       ├── notification.py       # NotificationPort
│       │       └── sync.py               # GitSyncPort
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── markdown_storage.py       # Obsidian vault persistence ✓
│       │   ├── whisper_stt.py            # Offline Speech-to-Text (faster-whisper)
│       │   ├── android_tts.py            # Text-to-Speech
│       │   ├── git_sync.py               # GitPython integration
│       │   └── notifications/
│       │       ├── __init__.py
│       │       ├── android.py            # Android push notifications
│       │       └── desktop.py            # Desktop notifications (for TUI)
│       └── ui/
│           ├── flet_app/
│           │   ├── __init__.py
│           │   ├── main.py               # Flet entry point
│           │   ├── screens/
│           │   │   ├── __init__.py
│           │   │   ├── home.py           # Main screen
│           │   │   ├── topic_select.py   # Topic selection
│           │   │   ├── dictation.py      # Dictation screen
│           │   │   └── settings.py       # Settings
│           │   └── components/
│           │       ├── __init__.py
│           │       ├── big_button.py     # Car-friendly large buttons
│           │       └── topic_chip.py     # Topic chips
│           └── tui/
│               ├── __init__.py
│               └── main.py               # Textual/Rich TUI
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_integration.py               # ✓
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── test_markdown_storage.py      # ✓
│   └── core/
│       ├── __init__.py
│       ├── test_topic_service.py         # ✓
│       ├── test_journal_service.py       # ✓
│       └── test_models.py                # ✓
├── vault/                                # Obsidian vault (gitignored)
│   ├── topics/                           # Topic markdown files
│   └── *.md                              # Daily notes
├── models/                               # Whisper models (gitignored)
├── main.py                               # Entry point, DI wiring
├── pyproject.toml
└── README.md
```

---

## 6. Resolved Decisions

| Question              | Decision                                                    |
| --------------------- | ----------------------------------------------------------- |
| Topic hierarchy?      | Flat for MVP, hierarchy later if needed                     |
| Offline STT engine?   | Whisper.cpp via `faster-whisper` (higher accuracy)          |
| Duplicate detection?  | Fuzzy matching with `rapidfuzz`                             |
| Git sync trigger?     | Manual only (fewer failure modes)                           |
| DI framework?         | None – manual wiring is sufficient                          |
| Data validation?      | Pydantic models                                             |
| Target platform?      | Android first (via Flet), Desktop second                    |

---

## 7. MVP Scope (Phase 1)

### Implementation Order

1. ~~**Storage first**: Implement MarkdownStorage adapter~~ ✓ DONE
2. ~~**Core models**: Pydantic models for Topic, JournalEntry, DailyNote~~ ✓ DONE
3. ~~**TopicService**: CRUD with fuzzy duplicate detection~~ ✓ DONE
4. ~~**JournalService**: Manage daily entries~~ ✓ DONE
5. ~~**Minimal Flet UI**: Topic list, add topic, basic navigation~~ ✓ DONE
6. **Whisper integration**: Start with file-based transcription, then streaming
7. **Evening flow**: Complete dictation and export workflow

### Included in MVP

- [x] Flet app with large, car-friendly buttons
- [x] Topic list (CRUD, flat, stored as Obsidian markdown)
- [x] Fuzzy duplicate detection with rapidfuzz
- [ ] Speech-to-text with Whisper (German, offline)
- [x] Direct Obsidian vault writing with `[[wiki links]]` and nested tags
- [ ] One configurable evening reminder
- [x] Core/UI separation (Ports & Adapters)

### Phase 2

- [ ] TTS instructions for car mode
- [ ] Git sync
- [ ] Daytime notifications (quick capture)
- [ ] Improved duplicate detection with aliases

### Phase 3

- [ ] Topic hierarchy
- [ ] TUI implementation
- [ ] Voice control for navigation

---

## 8. Technical Dependencies

Core:
- `pydantic>=2.0` - Data validation and serialization
- `rapidfuzz>=3.0` - Fuzzy string matching

UI:
- `flet>=0.25` - Cross-platform UI

Speech:
- `faster-whisper>=1.0` - Offline speech-to-text (Whisper.cpp bindings)
- `sounddevice>=0.5` - Audio recording

Sync:
- `gitpython>=3.1` - Git integration

Dev:
- `pytest>=8.0` - Testing
- `ruff>=0.8` - Linting and formatting

### Setup

```bash
# Install dev dependencies (required before running tests/linting)
uv sync --extra dev

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

---

## Appendix: Obsidian File Formats

### Daily Note (`2026-01-28.md`)

```markdown
---
tags:
  - lipi/daily
---

# 2026-01-28

## Topics of the Day

- [[Project Alpha]]
- [[Team Meeting]]
- [[Feature X Idea]]

## Notes

### [[Project Alpha]]

Finished the first prototype today. Performance isn't optimal yet,
but the basic functionality is working.

### [[Team Meeting]]

Discussion about next milestones. Deadline for v1.0 is end of February.

### [[Feature X Idea]]

Spontaneous idea during the drive: What if we could also embed
audio notes directly?

```

### Topic File (`topics/Project Alpha.md`)

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

### Tag Naming Convention

All tags use nested format under `lipi/` prefix:
- Topics: `lipi/topic/{sanitized_name}` (lowercase, spaces → underscores, alphanumeric only)
- Daily notes: `lipi/daily`
