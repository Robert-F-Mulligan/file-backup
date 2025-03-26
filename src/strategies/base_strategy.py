from abc import ABC, abstractmethod
from typing import Optional, List
import logging
from ..utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class FileHandlingStrategy(ABC):
    """Abstract base class for file handling strategies."""

    def __init__(self, operation: str = "copy"):
        """Initialize the strategy with a default operation of 'copy'."""
        self.operation = operation
        logger.info(f"Using '{self.operation}' operation for file handling.")

    @abstractmethod
    def build_destination_path(self, file_path: str) -> tuple:
        """Extract and return the year, month, and filename from the file path."""
        pass

    def execute_operation(self, operation: str, src_path: str, dest_path: str):
        """
        Execute the file operation (move/copy) dynamically.

        This ensures all strategies can perform file operations 
        without duplicating logic.
        """
        FileHandler.execute_operation(operation, src_path, dest_path)