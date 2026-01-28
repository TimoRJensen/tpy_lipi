"""Integration tests for the full workflow."""

from datetime import date
from pathlib import Path

from tpy_lipi.app import App


class TestFullWorkflow:
    """Test the complete journaling workflow."""

    def test_create_topics_and_add_entries(self, tmp_path: Path):
        """Full workflow: create topics, add mentions, add entries."""
        app = App(tmp_path)

        # Create some topics
        alpha = app.topics.create_topic("Project Alpha")
        beta = app.topics.create_topic("Project Beta")

        assert alpha.name == "Project Alpha"
        assert beta.name == "Project Beta"

        # Add topic mentions during the day
        app.journal.add_topic_mention("Project Alpha")
        app.journal.add_topic_mention("Project Beta")

        # Add detailed entries in the evening
        app.journal.add_entry("Project Alpha", "Made progress on the prototype.")
        app.journal.add_entry("Project Beta", "Had a productive meeting.")
        app.journal.add_entry("Project Alpha", "Fixed a critical bug.")

        # Verify the daily note
        today = app.journal.get_today()
        assert "Project Alpha" in today.topic_mentions
        assert "Project Beta" in today.topic_mentions
        assert len(today.entries) == 3

    def test_markdown_files_are_created_correctly(self, tmp_path: Path):
        """Verify that markdown files are created in the vault."""
        app = App(tmp_path)

        # Create a topic
        app.topics.create_topic("Test Topic")

        # Verify topic file exists
        topic_file = tmp_path / "topics" / "Test Topic.md"
        assert topic_file.exists()
        content = topic_file.read_text()
        assert "lipi/topic/" in content
        assert "# Test Topic" in content

    def test_daily_note_file_is_created(self, tmp_path: Path):
        """Verify that daily note file is created with correct format."""
        app = App(tmp_path)

        app.topics.create_topic("My Topic")
        app.journal.add_topic_mention("My Topic")
        app.journal.add_entry("My Topic", "Some notes here.")

        # Verify daily note file exists
        daily_file = tmp_path / f"{date.today().isoformat()}.md"
        assert daily_file.exists()
        content = daily_file.read_text()
        assert "lipi/daily" in content
        assert "[[My Topic]]" in content
        assert "Some notes here." in content

    def test_wiki_links_reference_topics(self, tmp_path: Path):
        """Verify that wiki links in daily notes reference existing topics."""
        app = App(tmp_path)

        # Create topic
        app.topics.create_topic("Linked Topic")

        # Add to journal
        app.journal.add_topic_mention("Linked Topic")

        # Read the daily note
        daily_file = tmp_path / f"{date.today().isoformat()}.md"
        content = daily_file.read_text()

        # Verify wiki link format
        assert "[[Linked Topic]]" in content

        # Verify topic file also exists (the link target)
        topic_file = tmp_path / "topics" / "Linked Topic.md"
        assert topic_file.exists()

    def test_duplicate_detection_works(self, tmp_path: Path):
        """Verify that duplicate detection finds similar topics."""
        app = App(tmp_path)

        app.topics.create_topic("Project Alpha")
        app.topics.create_topic("Project Beta")

        # Check for duplicates with a typo
        duplicates = app.topics.find_duplicates("Projekt Alpha")

        assert len(duplicates) >= 1
        assert any(d.name == "Project Alpha" for d in duplicates)
