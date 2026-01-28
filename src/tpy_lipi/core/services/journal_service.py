"""Journal management service."""

from datetime import date

from tpy_lipi.core.models import DailyNote, JournalEntry
from tpy_lipi.core.ports.storage import StoragePort
from tpy_lipi.core.services.topic_service import TopicService


class JournalService:
    """Service for managing daily journal entries."""

    def __init__(self, storage: StoragePort, topic_service: TopicService):
        """Initialize with storage adapter and topic service."""
        self.storage = storage
        self.topic_service = topic_service

    def get_today(self) -> DailyNote:
        """Get today's daily note, or return an empty one if none exists."""
        note = self.storage.get_daily_note(date.today())
        if note is None:
            return DailyNote(date=date.today())
        return note

    def get_or_create_today(self) -> DailyNote:
        """Get today's daily note, creating and persisting it if needed."""
        note = self.storage.get_daily_note(date.today())
        if note is None:
            note = DailyNote(date=date.today())
            self.storage.save_daily_note(note)
        return note

    def add_topic_mention(self, topic_name: str) -> None:
        """Add a topic mention to today's note.

        Also touches the topic to update its last_used timestamp.
        """
        note = self.get_or_create_today()

        # Don't add duplicates
        if topic_name not in note.topic_mentions:
            note.topic_mentions.append(topic_name)

        self.storage.save_daily_note(note)

        # Touch the topic to update last_used
        self.topic_service.touch_topic(topic_name)

    def add_entry(self, topic_name: str, content: str) -> JournalEntry:
        """Add a journal entry for a topic.

        Also adds the topic to mentions if not already there.
        """
        note = self.get_or_create_today()

        # Ensure topic is in mentions
        if topic_name not in note.topic_mentions:
            note.topic_mentions.append(topic_name)

        # Create and add the entry
        entry = JournalEntry(topic_name=topic_name, content=content)
        note.entries.append(entry)

        self.storage.save_daily_note(note)

        # Touch the topic
        self.topic_service.touch_topic(topic_name)

        return entry

    def list_entries_for_topic(self, topic_name: str) -> list[JournalEntry]:
        """List all entries for a specific topic from today's note."""
        note = self.get_today()
        return [e for e in note.entries if e.topic_name == topic_name]
