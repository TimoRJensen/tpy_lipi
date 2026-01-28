"""Application class for dependency injection wiring."""

from pathlib import Path

from tpy_lipi.adapters.markdown_storage import MarkdownStorage
from tpy_lipi.core.services.journal_service import JournalService
from tpy_lipi.core.services.topic_service import TopicService


class App:
    """Main application class that wires together all components."""

    def __init__(self, vault_path: Path):
        """Initialize the app with the path to the Obsidian vault.

        Args:
            vault_path: Path to the Obsidian vault directory.
        """
        self.vault_path = Path(vault_path)
        self.storage = MarkdownStorage(self.vault_path)
        self.topics = TopicService(self.storage)
        self.journal = JournalService(self.storage, self.topics)
