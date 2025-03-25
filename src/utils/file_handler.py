import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Utility class for file handling operations."""

    @staticmethod
    def ensure_directory_exists(path: str) -> None:
        """Ensure the destination directory exists."""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                logger.info(f"✅ Created directory: {path}")
        except PermissionError:
            logger.error(f"❌ Permission error creating directory: {path}")
        except Exception as e:
            logger.error(f"❌ Unexpected error creating directory: {e}")
    
    @staticmethod
    def move_file(src: str, dst: str) -> None:
        """Moves a file to the destination path."""
        try:
            os.rename(src, dst)  # `os.rename` is used here as it works both for moving within the same file system
            logger.info(f"✅ Moved: {src} ➡ {dst}")
        except FileNotFoundError:
            logger.error(f"❌ Source file '{src}' not found.")
        except PermissionError:
            logger.error(f"❌ Permission error when moving '{src}' to '{dst}'.")
        except Exception as e:
            logger.error(f"❌ Unexpected error moving file: {e}")
