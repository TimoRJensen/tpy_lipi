"""Tests for JournalService."""

from datetime import date, datetime
from pathlib import Path

from tpy_lipi.adapters.markdown_storage import MarkdownStorage
from tpy_lipi.core.models import Topic
from tpy_lipi.core.services.journal_service import JournalService
from tpy_lipi.core.services.topic_service import TopicService


class TestJournalServiceMentions:
    """Tests for topic mention operations."""

    def test_add_topic_mention_adds_to_today(self, tmp_path: Path):
        """add_topic_mention adds the topic to today's mentions."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        journal_service.add_topic_mention("Project Alpha")

        today = journal_service.get_today()
        assert "Project Alpha" in today.topic_mentions

    def test_add_topic_mention_creates_daily_note_if_not_exists(self, tmp_path: Path):
        """add_topic_mention creates a daily note for today if none exists."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        # No daily note exists yet
        assert storage.get_daily_note(date.today()) is None

        journal_service.add_topic_mention("Project Alpha")

        # Now it exists
        assert storage.get_daily_note(date.today()) is not None

    def test_add_topic_mention_touches_topic(self, tmp_path: Path):
        """add_topic_mention updates the topic's last_used timestamp."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)

        # Create topic with old last_used
        topic = Topic(name="Project Alpha", last_used=datetime(2020, 1, 1))
        storage.save_topic(topic)
        before = datetime.now()

        journal_service.add_topic_mention("Project Alpha")

        after = datetime.now()
        updated = topic_service.get_topic("Project Alpha")
        assert updated is not None
        assert updated.last_used is not None
        assert before <= updated.last_used <= after

    def test_add_topic_mention_does_not_duplicate(self, tmp_path: Path):
        """add_topic_mention doesn't add the same topic twice."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        journal_service.add_topic_mention("Project Alpha")
        journal_service.add_topic_mention("Project Alpha")

        today = journal_service.get_today()
        assert today.topic_mentions.count("Project Alpha") == 1


class TestJournalServiceEntries:
    """Tests for journal entry operations."""

    def test_add_entry_creates_journal_entry(self, tmp_path: Path):
        """add_entry creates a journal entry for the topic."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        entry = journal_service.add_entry("Project Alpha", "Made good progress today.")

        assert entry.topic_name == "Project Alpha"
        assert entry.content == "Made good progress today."

    def test_add_entry_persists_to_daily_note(self, tmp_path: Path):
        """add_entry saves the entry to today's daily note."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        journal_service.add_entry("Project Alpha", "Made good progress today.")

        today = journal_service.get_today()
        assert len(today.entries) == 1
        assert today.entries[0].content == "Made good progress today."

    def test_add_entry_also_adds_topic_mention(self, tmp_path: Path):
        """add_entry also adds the topic to mentions if not already there."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        journal_service.add_entry("Project Alpha", "Made good progress today.")

        today = journal_service.get_today()
        assert "Project Alpha" in today.topic_mentions


class TestJournalServiceGetToday:
    """Tests for getting today's note."""

    def test_get_today_returns_existing_note(self, tmp_path: Path):
        """get_today returns existing daily note for today."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")
        journal_service.add_topic_mention("Project Alpha")

        today = journal_service.get_today()

        assert today.date == date.today()
        assert "Project Alpha" in today.topic_mentions

    def test_get_today_returns_empty_note_if_none_exists(self, tmp_path: Path):
        """get_today returns an empty note if none exists for today."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)

        today = journal_service.get_today()

        assert today.date == date.today()
        assert today.topic_mentions == []
        assert today.entries == []

    def test_get_or_create_today_creates_and_saves(self, tmp_path: Path):
        """get_or_create_today creates and persists a new note if needed."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)

        # No note exists
        assert storage.get_daily_note(date.today()) is None

        today = journal_service.get_or_create_today()

        # Now it's persisted
        assert storage.get_daily_note(date.today()) is not None
        assert today.date == date.today()


class TestJournalServiceListEntries:
    """Tests for listing entries by topic."""

    def test_list_entries_for_topic_returns_matching_entries(self, tmp_path: Path):
        """list_entries_for_topic returns entries for a specific topic."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")
        topic_service.create_topic("Project Beta")

        journal_service.add_entry("Project Alpha", "Alpha note 1")
        journal_service.add_entry("Project Beta", "Beta note")
        journal_service.add_entry("Project Alpha", "Alpha note 2")

        alpha_entries = journal_service.list_entries_for_topic("Project Alpha")

        assert len(alpha_entries) == 2
        contents = {e.content for e in alpha_entries}
        assert contents == {"Alpha note 1", "Alpha note 2"}

    def test_list_entries_for_topic_returns_empty_for_no_matches(self, tmp_path: Path):
        """list_entries_for_topic returns empty list when no entries match."""
        storage = MarkdownStorage(tmp_path)
        topic_service = TopicService(storage)
        journal_service = JournalService(storage, topic_service)
        topic_service.create_topic("Project Alpha")

        entries = journal_service.list_entries_for_topic("Project Alpha")

        assert entries == []
