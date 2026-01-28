"""Domain models for tpy_lipi."""

import re
from datetime import date, datetime
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Topic(BaseModel):
    """A topic/theme that can be referenced in daily notes."""

    name: str
    aliases: list[str] = Field(default_factory=list)
    last_used: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Topic name cannot be empty")
        return v.strip()

    def _tag_name(self) -> str:
        """Convert topic name to valid Obsidian tag format.

        Rules: lowercase, spaces to underscores, remove special characters.
        """
        tag = self.name.lower()
        tag = tag.replace(" ", "_")
        tag = re.sub(r"[^a-z0-9_]", "", tag)
        return tag

    def to_markdown(self) -> str:
        """Serialize topic to Obsidian-compatible markdown with frontmatter."""
        lines = ["---", "tags:", f"  - lipi/topic/{self._tag_name()}"]

        # Aliases
        if self.aliases:
            lines.append("aliases:")
            for alias in self.aliases:
                lines.append(f"  - {alias}")
        else:
            lines.append("aliases: []")

        # Timestamps
        if self.last_used:
            lines.append(f"last_used: {self.last_used.isoformat()}")
        lines.append(f"created_at: {self.created_at.isoformat()}")

        lines.append("---")
        lines.append("")
        lines.append(f"# {self.name}")
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, content: str, name: str) -> Self:
        """Parse topic from markdown with frontmatter."""
        # Extract frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError("No frontmatter found")

        frontmatter = frontmatter_match.group(1)

        # Parse aliases
        aliases: list[str] = []
        aliases_match = re.search(r"aliases:\s*\n((?:\s+-\s+.+\n)*)", frontmatter)
        if aliases_match:
            alias_lines = aliases_match.group(1)
            aliases = re.findall(r"-\s+(.+)", alias_lines)

        # Parse last_used
        last_used: datetime | None = None
        last_used_match = re.search(r"last_used:\s*(.+)", frontmatter)
        if last_used_match:
            last_used = datetime.fromisoformat(last_used_match.group(1).strip())

        # Parse created_at
        created_at_match = re.search(r"created_at:\s*(.+)", frontmatter)
        if not created_at_match:
            raise ValueError("created_at is required")
        created_at = datetime.fromisoformat(created_at_match.group(1).strip())

        return cls(
            name=name,
            aliases=aliases,
            last_used=last_used,
            created_at=created_at,
        )


class JournalEntry(BaseModel):
    """A detailed note entry for a topic within a daily note."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    topic_name: str
    content: str
    recorded_at: datetime = Field(default_factory=datetime.now)


class DailyNote(BaseModel):
    """A daily journal note containing topic mentions and detailed entries."""

    date: date
    topic_mentions: list[str] = Field(default_factory=list)
    entries: list[JournalEntry] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Serialize daily note to Obsidian-compatible markdown."""
        lines = [
            "---",
            "tags:",
            "  - lipi/daily",
            "---",
            "",
            f"# {self.date.isoformat()}",
        ]

        # Topics of the Day section
        if self.topic_mentions:
            lines.append("")
            lines.append("## Topics of the Day")
            lines.append("")
            for topic in self.topic_mentions:
                lines.append(f"- [[{topic}]]")

        # Notes section with entries
        if self.entries:
            lines.append("")
            lines.append("## Notes")

            # Group entries by topic
            entries_by_topic: dict[str, list[JournalEntry]] = {}
            for entry in self.entries:
                if entry.topic_name not in entries_by_topic:
                    entries_by_topic[entry.topic_name] = []
                entries_by_topic[entry.topic_name].append(entry)

            for topic_name, topic_entries in entries_by_topic.items():
                lines.append("")
                lines.append(f"### [[{topic_name}]]")
                for entry in topic_entries:
                    lines.append("")
                    lines.append(f"<!-- entry:{entry.id} -->")
                    lines.append(entry.content)

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, content: str, note_date: date) -> Self:
        """Parse daily note from markdown."""
        topic_mentions: list[str] = []
        entries: list[JournalEntry] = []

        # Extract topic mentions from "Topics of the Day" section
        topics_section = re.search(
            r"## Topics of the Day\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if topics_section:
            mentions = re.findall(r"\[\[(.+?)\]\]", topics_section.group(1))
            topic_mentions = mentions

        # Extract entries from "Notes" section
        notes_section = re.search(r"## Notes\s*\n(.*?)(?=\Z)", content, re.DOTALL)
        if notes_section:
            notes_content = notes_section.group(1)
            # Find each topic heading and its content
            topic_pattern = r"### \[\[(.+?)\]\]\s*\n(.*?)(?=\n### |\Z)"
            for match in re.finditer(topic_pattern, notes_content, re.DOTALL):
                topic_name = match.group(1)
                topic_content = match.group(2)

                # Check for entry markers
                entry_pattern = r"<!-- entry:([a-f0-9-]+) -->\s*\n(.*?)(?=\n<!-- entry:|\Z)"
                entry_matches = list(re.finditer(entry_pattern, topic_content, re.DOTALL))

                if entry_matches:
                    # Parse individual entries
                    for entry_match in entry_matches:
                        entry_id = entry_match.group(1)
                        entry_content = entry_match.group(2).strip()
                        if entry_content:
                            entries.append(
                                JournalEntry(
                                    id=entry_id,
                                    topic_name=topic_name,
                                    content=entry_content,
                                )
                            )
                else:
                    # No entry markers - treat entire content as single entry
                    entry_content = topic_content.strip()
                    if entry_content:
                        entries.append(
                            JournalEntry(
                                topic_name=topic_name,
                                content=entry_content,
                            )
                        )

        return cls(
            date=note_date,
            topic_mentions=topic_mentions,
            entries=entries,
        )
