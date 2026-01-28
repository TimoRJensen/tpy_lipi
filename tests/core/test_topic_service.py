"""Tests for TopicService."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tpy_lipi.adapters.markdown_storage import MarkdownStorage
from tpy_lipi.core.models import Topic
from tpy_lipi.core.services.topic_service import TopicService


class TestTopicServiceCreate:
    """Tests for creating topics."""

    def test_create_topic_returns_topic(self, tmp_path: Path):
        """create_topic returns the created topic."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)

        topic = service.create_topic("Project Alpha")

        assert topic.name == "Project Alpha"

    def test_create_topic_saves_to_storage(self, tmp_path: Path):
        """create_topic persists the topic to storage."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)

        service.create_topic("Project Alpha")

        # Verify it's persisted
        assert storage.get_topic("Project Alpha") is not None

    def test_create_topic_sets_last_used_to_now(self, tmp_path: Path):
        """create_topic sets last_used to current time."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        before = datetime.now()

        topic = service.create_topic("Project Alpha")

        after = datetime.now()
        assert topic.last_used is not None
        assert before <= topic.last_used <= after

    def test_create_topic_rejects_empty_name(self, tmp_path: Path):
        """create_topic raises ValueError for empty name."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)

        with pytest.raises(ValueError):
            service.create_topic("")


class TestTopicServiceGet:
    """Tests for retrieving topics."""

    def test_get_topic_returns_topic(self, tmp_path: Path):
        """get_topic retrieves an existing topic."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("Project Alpha")

        topic = service.get_topic("Project Alpha")

        assert topic is not None
        assert topic.name == "Project Alpha"

    def test_get_topic_returns_none_when_not_found(self, tmp_path: Path):
        """get_topic returns None for non-existent topic."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)

        topic = service.get_topic("Nonexistent")

        assert topic is None


class TestTopicServiceList:
    """Tests for listing topics."""

    def test_list_topics_returns_all_topics(self, tmp_path: Path):
        """list_topics returns all created topics."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("Topic A")
        service.create_topic("Topic B")
        service.create_topic("Topic C")

        topics = service.list_topics()

        assert len(topics) == 3
        names = {t.name for t in topics}
        assert names == {"Topic A", "Topic B", "Topic C"}

    def test_list_recent_topics_filters_by_last_used(self, tmp_path: Path):
        """list_recent_topics only returns recently used topics."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)

        # Create topics with different last_used times
        recent = Topic(name="Recent", last_used=datetime.now())
        old = Topic(name="Old", last_used=datetime.now() - timedelta(days=30))
        storage.save_topic(recent)
        storage.save_topic(old)

        result = service.list_recent_topics(days=14)

        assert len(result) == 1
        assert result[0].name == "Recent"


class TestTopicServiceDelete:
    """Tests for deleting topics."""

    def test_delete_topic_removes_topic(self, tmp_path: Path):
        """delete_topic removes the topic from storage."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("To Delete")

        service.delete_topic("To Delete")

        assert service.get_topic("To Delete") is None


class TestTopicServiceDuplicates:
    """Tests for duplicate detection."""

    def test_find_duplicates_returns_similar_names(self, tmp_path: Path):
        """find_duplicates returns topics with similar names."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("Project Alpha")
        service.create_topic("Project Beta")
        service.create_topic("Something Else")

        duplicates = service.find_duplicates("Project Alfa")  # typo

        assert len(duplicates) >= 1
        names = {t.name for t in duplicates}
        assert "Project Alpha" in names

    def test_find_duplicates_checks_aliases(self, tmp_path: Path):
        """find_duplicates also matches against aliases."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        topic = Topic(name="Project Alpha", aliases=["Alpha", "PA"])
        storage.save_topic(topic)

        duplicates = service.find_duplicates("Alpha")

        assert len(duplicates) == 1
        assert duplicates[0].name == "Project Alpha"

    def test_find_duplicates_respects_threshold(self, tmp_path: Path):
        """find_duplicates uses the threshold parameter."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("Project Alpha")

        # Very different name should not match with high threshold
        duplicates = service.find_duplicates("Completely Different", threshold=90)

        assert len(duplicates) == 0

    def test_find_duplicates_returns_empty_for_no_matches(self, tmp_path: Path):
        """find_duplicates returns empty list when no matches."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        service.create_topic("Project Alpha")

        duplicates = service.find_duplicates("Xyz123")

        assert duplicates == []


class TestTopicServiceTouch:
    """Tests for touching topics."""

    def test_touch_topic_updates_last_used(self, tmp_path: Path):
        """touch_topic updates the last_used timestamp."""
        storage = MarkdownStorage(tmp_path)
        service = TopicService(storage)
        topic = Topic(name="Project Alpha", last_used=datetime(2020, 1, 1))
        storage.save_topic(topic)
        before = datetime.now()

        service.touch_topic("Project Alpha")

        after = datetime.now()
        updated = service.get_topic("Project Alpha")
        assert updated is not None
        assert updated.last_used is not None
        assert before <= updated.last_used <= after
