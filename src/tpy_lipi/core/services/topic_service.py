"""Topic management service."""

from datetime import datetime

from rapidfuzz import fuzz

from tpy_lipi.core.models import Topic
from tpy_lipi.core.ports.storage import StoragePort


class TopicService:
    """Service for managing topics."""

    def __init__(self, storage: StoragePort):
        """Initialize with a storage adapter."""
        self.storage = storage

    def create_topic(self, name: str) -> Topic:
        """Create a new topic with the given name."""
        topic = Topic(name=name, last_used=datetime.now())
        self.storage.save_topic(topic)
        return topic

    def get_topic(self, name: str) -> Topic | None:
        """Get a topic by name."""
        return self.storage.get_topic(name)

    def list_topics(self) -> list[Topic]:
        """List all topics."""
        return self.storage.get_all_topics()

    def list_recent_topics(self, days: int = 14) -> list[Topic]:
        """List topics used within the last N days."""
        return self.storage.get_recent_topics(days)

    def delete_topic(self, name: str) -> None:
        """Delete a topic by name."""
        self.storage.delete_topic(name)

    def find_duplicates(self, name: str, threshold: int = 80) -> list[Topic]:
        """Find topics with similar names or aliases.

        Args:
            name: The name to check for duplicates.
            threshold: Minimum fuzzy match score (0-100) to consider a duplicate.

        Returns:
            List of topics that match above the threshold.
        """
        all_topics = self.storage.get_all_topics()
        duplicates: list[Topic] = []

        for topic in all_topics:
            # Check against topic name
            name_score = fuzz.ratio(name.lower(), topic.name.lower())
            if name_score >= threshold:
                duplicates.append(topic)
                continue

            # Check against aliases
            for alias in topic.aliases:
                alias_score = fuzz.ratio(name.lower(), alias.lower())
                if alias_score >= threshold:
                    duplicates.append(topic)
                    break

        return duplicates

    def touch_topic(self, name: str) -> None:
        """Update the last_used timestamp for a topic."""
        topic = self.storage.get_topic(name)
        if topic:
            topic.last_used = datetime.now()
            self.storage.save_topic(topic)
