import os
import shutil
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Utility class for file handling operations."""

    @staticmethod
    def execute_operation(operation: str, src: str, dest: str):
        """Execute the file operation (move/copy) dynamically using a dictionary dispatch."""
        operations = {
            "move": FileHandler.move_file,
            "copy": FileHandler.copy_file
        }
        
        operation_func = operations.get(operation)
        if not operation_func:
            raise ValueError(f"Unsupported operation: {operation}")

        operation_func(src, dest)  # Call the appropriate function

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
    def is_temporary_file(file_path: str) -> bool:
        """Checks if a file is a temporary file."""
        return file_path.endswith(".TMP") or file_path.startswith("~$")
    
    @staticmethod
    def move_file(src: str, dest: str):
        """Move a file to a new location."""
        try:
            FileHandler.ensure_directory_exists(os.path.dirname(dest))
            shutil.move(src, dest)
            logger.info(f"📂 Moved file: {src} ➝ {dest}")
        except Exception as e:
            logger.error(f"❌ Error moving file {src} to {dest}: {e}")
            raise

    @staticmethod
    def copy_file(src: str, dest: str):
        """Copy a file to a new location."""
        try:
            FileHandler.ensure_directory_exists(os.path.dirname(dest))
            shutil.copy2(src, dest)  # copy2 preserves metadata
            logger.info(f"📄 Copied file: {src} ➝ {dest}")
        except Exception as e:
            logger.error(f"❌ Error copying file {src} to {dest}: {e}")
            raise
