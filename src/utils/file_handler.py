import os
import shutil
import hashlib
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Utility class for file handling operations."""

    @staticmethod
    def execute_operation(operation: str, src: str, dest: str):
        """Execute the file operation (move/copy) dynamically using a dictionary dispatch."""
        
        logger.info(f"Attempting to {operation} file from {src} to {dest}")

        operations = {
            "move": FileHandler.move_file,
            "copy": FileHandler.copy_file,
            "sync": FileHandler.sync_file
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

    @staticmethod
    def sync_file(src: str, dest: str):
        """Sync file: copy only if the source has changed or the destination doesn't exist."""
        if FileHandler.is_file_modified(src, dest):
            logger.info(f"📤 Syncing file: {src} ➝ {dest}")
            FileHandler.copy_file(src, dest)
        else:
            logger.info(f"✔️ File {src} is already in sync with {dest}. Skipping.")

    @staticmethod
    def is_file_modified(src: str, dest: str) -> bool:
        """Check if the file has been modified by comparing hashes."""
        if not os.path.exists(dest):
            logger.info(f"❗ Destination file {dest} does not exist. Syncing.")
            return True
        
        # Compare file hashes
        source_hash = FileHandler.calculate_file_hash(src)
        dest_hash = FileHandler.calculate_file_hash(dest)

        if source_hash != dest_hash:
            logger.info(f"❗ File {src} has been modified. Syncing.")
            return True
        
        return False

    @staticmethod
    def calculate_file_hash(file_path: str, hash_algo: str = 'sha256') -> str:
        """Calculate the hash of a file's contents."""
        hash_func = hashlib.new(hash_algo)
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error reading file {file_path} for hashing: {e}")
            raise
