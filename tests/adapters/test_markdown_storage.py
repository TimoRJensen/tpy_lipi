"""Tests for MarkdownStorage adapter."""

from datetime import date, datetime, timedelta
from pathlib import Path

from tpy_lipi.adapters.markdown_storage import MarkdownStorage
from tpy_lipi.core.models import DailyNote, JournalEntry, Topic


class TestMarkdownStorageTopics:
    """Tests for topic operations in MarkdownStorage."""

    def test_save_topic_creates_file(self, tmp_path: Path):
        """save_topic creates a markdown file in topics directory."""
        storage = MarkdownStorage(tmp_path)
        topic = Topic(name="Project Alpha")

        storage.save_topic(topic)

        topic_file = tmp_path / "topics" / "Project Alpha.md"
        assert topic_file.exists()

    def test_save_topic_includes_frontmatter(self, tmp_path: Path):
        """save_topic creates file with correct frontmatter."""
        storage = MarkdownStorage(tmp_path)
        topic = Topic(
            name="Project Alpha",
            aliases=["Alpha"],
            created_at=datetime(2026, 1, 28, 10, 0, 0),
        )

        storage.save_topic(topic)

        content = (tmp_path / "topics" / "Project Alpha.md").read_text()
        assert "lipi/topic/" in content
        assert "aliases:" in content
        assert "Alpha" in content
        assert "# Project Alpha" in content

    def test_get_topic_returns_topic(self, tmp_path: Path):
        """get_topic retrieves a saved topic."""
        storage = MarkdownStorage(tmp_path)
        topic = Topic(
            name="Project Alpha",
            aliases=["Alpha"],
            created_at=datetime(2026, 1, 28, 10, 0, 0),
        )
        storage.save_topic(topic)

        result = storage.get_topic("Project Alpha")

        assert result is not None
        assert result.name == "Project Alpha"
        assert result.aliases == ["Alpha"]

    def test_get_topic_returns_none_when_not_found(self, tmp_path: Path):
        """get_topic returns None for non-existent topic."""
        storage = MarkdownStorage(tmp_path)

        result = storage.get_topic("Nonexistent")

        assert result is None

    def test_get_all_topics_returns_empty_list_initially(self, tmp_path: Path):
        """get_all_topics returns empty list when no topics exist."""
        storage = MarkdownStorage(tmp_path)

        result = storage.get_all_topics()

        assert result == []

    def test_get_all_topics_returns_all_topics(self, tmp_path: Path):
        """get_all_topics returns all saved topics."""
        storage = MarkdownStorage(tmp_path)
        storage.save_topic(Topic(name="Topic A"))
        storage.save_topic(Topic(name="Topic B"))
        storage.save_topic(Topic(name="Topic C"))

        result = storage.get_all_topics()

        assert len(result) == 3
        names = {t.name for t in result}
        assert names == {"Topic A", "Topic B", "Topic C"}

    def test_get_recent_topics_filters_by_last_used(self, tmp_path: Path):
        """get_recent_topics only returns topics used within N days."""
        storage = MarkdownStorage(tmp_path)
        now = datetime.now()

        # Topic used recently
        recent = Topic(name="Recent", last_used=now)
        storage.save_topic(recent)

        # Topic used 30 days ago
        old = Topic(name="Old", last_used=now - timedelta(days=30))
        storage.save_topic(old)

        # Topic never used
        never = Topic(name="Never")
        storage.save_topic(never)

        result = storage.get_recent_topics(days=14)

        assert len(result) == 1
        assert result[0].name == "Recent"

    def test_delete_topic_removes_file(self, tmp_path: Path):
        """delete_topic removes the topic markdown file."""
        storage = MarkdownStorage(tmp_path)
        storage.save_topic(Topic(name="To Delete"))

        storage.delete_topic("To Delete")

        assert not (tmp_path / "topics" / "To Delete.md").exists()
        assert storage.get_topic("To Delete") is None

    def test_handles_special_characters_in_name(self, tmp_path: Path):
        """Topic names with special characters are sanitized for filenames."""
        storage = MarkdownStorage(tmp_path)
        topic = Topic(name="Project: Alpha/Beta")

        storage.save_topic(topic)
        result = storage.get_topic("Project: Alpha/Beta")

        assert result is not None
        assert result.name == "Project: Alpha/Beta"


class TestMarkdownStorageDailyNotes:
    """Tests for daily note operations in MarkdownStorage."""

    def test_save_daily_note_creates_file(self, tmp_path: Path):
        """save_daily_note creates a markdown file with date as filename."""
        storage = MarkdownStorage(tmp_path)
        note = DailyNote(date=date(2026, 1, 28))

        storage.save_daily_note(note)

        note_file = tmp_path / "2026-01-28.md"
        assert note_file.exists()

    def test_save_daily_note_includes_frontmatter(self, tmp_path: Path):
        """save_daily_note creates file with correct frontmatter."""
        storage = MarkdownStorage(tmp_path)
        note = DailyNote(
            date=date(2026, 1, 28),
            topic_mentions=["Project Alpha"],
        )

        storage.save_daily_note(note)

        content = (tmp_path / "2026-01-28.md").read_text()
        assert "lipi/daily" in content
        assert "[[Project Alpha]]" in content

    def test_get_daily_note_returns_note(self, tmp_path: Path):
        """get_daily_note retrieves a saved daily note."""
        storage = MarkdownStorage(tmp_path)
        note = DailyNote(
            date=date(2026, 1, 28),
            topic_mentions=["Project Alpha", "Team Meeting"],
        )
        storage.save_daily_note(note)

        result = storage.get_daily_note(date(2026, 1, 28))

        assert result is not None
        assert result.date == date(2026, 1, 28)
        assert "Project Alpha" in result.topic_mentions

    def test_get_daily_note_returns_none_when_not_found(self, tmp_path: Path):
        """get_daily_note returns None for non-existent date."""
        storage = MarkdownStorage(tmp_path)

        result = storage.get_daily_note(date(2026, 1, 28))

        assert result is None

    def test_get_daily_notes_range_returns_notes_in_range(self, tmp_path: Path):
        """get_daily_notes_range returns only notes within date range."""
        storage = MarkdownStorage(tmp_path)
        storage.save_daily_note(DailyNote(date=date(2026, 1, 25)))
        storage.save_daily_note(DailyNote(date=date(2026, 1, 26)))
        storage.save_daily_note(DailyNote(date=date(2026, 1, 27)))
        storage.save_daily_note(DailyNote(date=date(2026, 1, 28)))
        storage.save_daily_note(DailyNote(date=date(2026, 1, 29)))

        result = storage.get_daily_notes_range(date(2026, 1, 26), date(2026, 1, 28))

        assert len(result) == 3
        dates = {n.date for n in result}
        assert dates == {date(2026, 1, 26), date(2026, 1, 27), date(2026, 1, 28)}

    def test_save_daily_note_with_entries(self, tmp_path: Path):
        """save_daily_note preserves journal entries."""
        storage = MarkdownStorage(tmp_path)
        entry = JournalEntry(
            topic_name="Project Alpha",
            content="Made progress on feature X.",
        )
        note = DailyNote(
            date=date(2026, 1, 28),
            topic_mentions=["Project Alpha"],
            entries=[entry],
        )

        storage.save_daily_note(note)
        result = storage.get_daily_note(date(2026, 1, 28))

        assert result is not None
        assert len(result.entries) == 1
        assert result.entries[0].topic_name == "Project Alpha"
        assert "Made progress on feature X." in result.entries[0].content
