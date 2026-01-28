"""Tests for domain models."""

from datetime import date, datetime

import pytest

from tpy_lipi.core.models import DailyNote, JournalEntry, Topic


class TestTopic:
    """Tests for Topic model."""

    def test_create_topic_with_name(self):
        """Topic can be created with just a name."""
        topic = Topic(name="Project Alpha")
        assert topic.name == "Project Alpha"

    def test_topic_has_created_at_by_default(self):
        """Topic gets created_at timestamp automatically."""
        topic = Topic(name="Test")
        assert topic.created_at is not None
        assert isinstance(topic.created_at, datetime)

    def test_topic_has_empty_aliases_by_default(self):
        """Topic aliases default to empty list."""
        topic = Topic(name="Test")
        assert topic.aliases == []

    def test_topic_last_used_is_none_by_default(self):
        """Topic last_used is None initially."""
        topic = Topic(name="Test")
        assert topic.last_used is None

    def test_topic_name_cannot_be_empty(self):
        """Topic name cannot be empty string."""
        with pytest.raises(ValueError):
            Topic(name="")

    def test_topic_name_cannot_be_whitespace_only(self):
        """Topic name cannot be just whitespace."""
        with pytest.raises(ValueError):
            Topic(name="   ")

    def test_topic_to_markdown(self):
        """Topic can be serialized to markdown with frontmatter."""
        topic = Topic(
            name="Project Alpha",
            aliases=["Alpha", "PA"],
            created_at=datetime(2026, 1, 28, 10, 0, 0),
            last_used=datetime(2026, 1, 28, 14, 30, 0),
        )
        md = topic.to_markdown()

        assert "tags:" in md
        assert "lipi/topic/project_alpha" in md
        assert "aliases:" in md
        assert "Alpha" in md
        assert "PA" in md
        assert "last_used:" in md
        assert "created_at:" in md
        assert "# Project Alpha" in md

    def test_topic_from_markdown(self):
        """Topic can be parsed from markdown with frontmatter."""
        markdown = """---
tags:
  - lipi/topic/project_alpha
aliases:
  - Alpha
  - PA
last_used: 2026-01-28T14:30:00
created_at: 2026-01-28T10:00:00
---

# Project Alpha

Some notes here.
"""
        topic = Topic.from_markdown(markdown, name="Project Alpha")

        assert topic.name == "Project Alpha"
        assert topic.aliases == ["Alpha", "PA"]
        assert topic.last_used == datetime(2026, 1, 28, 14, 30, 0)
        assert topic.created_at == datetime(2026, 1, 28, 10, 0, 0)

    def test_topic_from_markdown_without_optional_fields(self):
        """Topic can be parsed when optional fields are missing."""
        markdown = """---
tags:
  - lipi/topic/test_topic
created_at: 2026-01-28T10:00:00
---

# Test Topic
"""
        topic = Topic.from_markdown(markdown, name="Test Topic")

        assert topic.name == "Test Topic"
        assert topic.aliases == []
        assert topic.last_used is None


class TestJournalEntry:
    """Tests for JournalEntry model."""

    def test_create_journal_entry(self):
        """JournalEntry can be created with topic_name and content."""
        entry = JournalEntry(topic_name="Project Alpha", content="Did some work today.")
        assert entry.topic_name == "Project Alpha"
        assert entry.content == "Did some work today."

    def test_journal_entry_has_id_by_default(self):
        """JournalEntry gets a UUID id automatically."""
        entry = JournalEntry(topic_name="Test", content="Content")
        assert entry.id is not None
        assert len(entry.id) == 36  # UUID format

    def test_journal_entry_has_recorded_at_by_default(self):
        """JournalEntry gets recorded_at timestamp automatically."""
        entry = JournalEntry(topic_name="Test", content="Content")
        assert entry.recorded_at is not None
        assert isinstance(entry.recorded_at, datetime)


class TestDailyNote:
    """Tests for DailyNote model."""

    def test_create_daily_note_with_date(self):
        """DailyNote can be created with just a date."""
        note = DailyNote(date=date(2026, 1, 28))
        assert note.date == date(2026, 1, 28)

    def test_daily_note_has_empty_mentions_by_default(self):
        """DailyNote topic_mentions defaults to empty list."""
        note = DailyNote(date=date(2026, 1, 28))
        assert note.topic_mentions == []

    def test_daily_note_has_empty_entries_by_default(self):
        """DailyNote entries defaults to empty list."""
        note = DailyNote(date=date(2026, 1, 28))
        assert note.entries == []

    def test_daily_note_to_markdown_empty(self):
        """Empty DailyNote generates valid markdown."""
        note = DailyNote(date=date(2026, 1, 28))
        md = note.to_markdown()

        assert "tags:" in md
        assert "lipi/daily" in md
        assert "# 2026-01-28" in md

    def test_daily_note_to_markdown_with_mentions(self):
        """DailyNote with topic mentions includes wiki links."""
        note = DailyNote(
            date=date(2026, 1, 28),
            topic_mentions=["Project Alpha", "Team Meeting"],
        )
        md = note.to_markdown()

        assert "[[Project Alpha]]" in md
        assert "[[Team Meeting]]" in md

    def test_daily_note_to_markdown_with_entries(self):
        """DailyNote with entries includes content under topic headings."""
        entry = JournalEntry(
            id="test-id",
            topic_name="Project Alpha",
            content="Made good progress today.",
            recorded_at=datetime(2026, 1, 28, 18, 0, 0),
        )
        note = DailyNote(
            date=date(2026, 1, 28),
            topic_mentions=["Project Alpha"],
            entries=[entry],
        )
        md = note.to_markdown()

        assert "### [[Project Alpha]]" in md
        assert "Made good progress today." in md

    def test_daily_note_from_markdown(self):
        """DailyNote can be parsed from markdown."""
        markdown = """---
tags:
  - lipi/daily
---

# 2026-01-28

## Topics of the Day

- [[Project Alpha]]
- [[Team Meeting]]

## Notes

### [[Project Alpha]]

Made good progress today.
"""
        note = DailyNote.from_markdown(markdown, note_date=date(2026, 1, 28))

        assert note.date == date(2026, 1, 28)
        assert "Project Alpha" in note.topic_mentions
        assert "Team Meeting" in note.topic_mentions
        assert len(note.entries) == 1
        assert note.entries[0].topic_name == "Project Alpha"
        assert "Made good progress today." in note.entries[0].content
