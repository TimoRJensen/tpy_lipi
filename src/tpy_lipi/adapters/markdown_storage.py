"""Markdown-based storage adapter for Obsidian vault."""

import re
from datetime import date, datetime, timedelta
from pathlib import Path

from tpy_lipi.core.models import DailyNote, Topic


class MarkdownStorage:
    """Storage adapter that persists data as Obsidian-compatible markdown files."""

    def __init__(self, vault_path: Path):
        """Initialize storage with path to Obsidian vault."""
        self.vault_path = Path(vault_path)
        self.topics_path = self.vault_path / "topics"

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use as a filename."""
        # Replace characters that are invalid in filenames
        invalid_chars = r'[<>:"/\\|?*]'
        return re.sub(invalid_chars, "_", name)

    def _topic_file_path(self, name: str) -> Path:
        """Get the file path for a topic."""
        safe_name = self._sanitize_filename(name)
        return self.topics_path / f"{safe_name}.md"

    def _daily_note_file_path(self, note_date: date) -> Path:
        """Get the file path for a daily note."""
        return self.vault_path / f"{note_date.isoformat()}.md"

    # Topic operations

    def save_topic(self, topic: Topic) -> None:
        """Save a topic as a markdown file."""
        self.topics_path.mkdir(parents=True, exist_ok=True)
        file_path = self._topic_file_path(topic.name)
        file_path.write_text(topic.to_markdown(), encoding="utf-8")

    def get_topic(self, name: str) -> Topic | None:
        """Get a topic by name."""
        file_path = self._topic_file_path(name)
        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")
        return Topic.from_markdown(content, name=name)

    def get_all_topics(self) -> list[Topic]:
        """Get all topics."""
        if not self.topics_path.exists():
            return []

        topics: list[Topic] = []
        for file_path in self.topics_path.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            # Extract name from the file - look for # heading
            name_match = re.search(r"^# (.+)$", content, re.MULTILINE)
            if name_match:
                name = name_match.group(1)
                try:
                    topic = Topic.from_markdown(content, name=name)
                    topics.append(topic)
                except ValueError:
                    # Skip files that can't be parsed
                    pass
        return topics

    def get_recent_topics(self, days: int = 14) -> list[Topic]:
        """Get topics used within the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        all_topics = self.get_all_topics()
        return [
            topic
            for topic in all_topics
            if topic.last_used is not None and topic.last_used >= cutoff
        ]

    def delete_topic(self, name: str) -> None:
        """Delete a topic by name."""
        file_path = self._topic_file_path(name)
        if file_path.exists():
            file_path.unlink()

    # DailyNote operations

    def save_daily_note(self, note: DailyNote) -> None:
        """Save a daily note as a markdown file."""
        self.vault_path.mkdir(parents=True, exist_ok=True)
        file_path = self._daily_note_file_path(note.date)
        file_path.write_text(note.to_markdown(), encoding="utf-8")

    def get_daily_note(self, note_date: date) -> DailyNote | None:
        """Get a daily note by date."""
        file_path = self._daily_note_file_path(note_date)
        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")
        return DailyNote.from_markdown(content, note_date=note_date)

    def get_daily_notes_range(self, start: date, end: date) -> list[DailyNote]:
        """Get daily notes within a date range (inclusive)."""
        notes: list[DailyNote] = []
        current = start
        while current <= end:
            note = self.get_daily_note(current)
            if note:
                notes.append(note)
            current += timedelta(days=1)
        return notes
