from abc import ABC, abstractmethod
from typing import Optional, List


class FileHandlingStrategy(ABC):
    """Abstract base class for file handling strategies."""

    @abstractmethod
    def build_destination_path(self, file_path: str) -> tuple:
        """Extract and return the year, month, and filename from the file path."""
        pass

    @abstractmethod
    def move_file(self, src: str, dst: str) -> None:
        """Move a file from the source to the destination."""
        pass