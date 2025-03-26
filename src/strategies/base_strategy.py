from abc import ABC, abstractmethod
from typing import Optional, List


class FileHandlingStrategy(ABC):
    """Abstract base class for file handling strategies."""

    @abstractmethod
    def build_destination_path(self, file_path: str) -> tuple:
        """Extract and return the year, month, and filename from the file path."""
        pass

    def move_file(self, src: str, dst: str) -> None:
        """Move a file from source to destination."""
        try:
            shutil.move(src, dst)
            logger.info(f"✅ Moved file: {src} ➡ {dst}")
        except Exception as e:
            logger.error(f"❌ Error moving file: {e}")

    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from source to destination."""
        try:
            shutil.copy2(src, dst)
            logger.info(f"✅ Copied file: {src} ➡ {dst}")
        except Exception as e:
            logger.error(f"❌ Error copying file: {e}")

    def execute_operation(self, operation: str, src: str, dst: str) -> None:
        """Dynamically select and execute the correct file operation."""
        operation_methods = {
            "move": self.move_file,
            "copy": self.copy_file,
        }

        operation_func = operation_methods.get(operation)

        if operation_func:
            operation_func(src, dst)
        else:
            logger.error(f"❌ Unsupported operation: {operation}")