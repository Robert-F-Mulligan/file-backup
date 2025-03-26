import os
import logging
from typing import Optional, List
from watchdog.events import FileSystemEventHandler
from ..utils.file_handler import FileHandler
from ..utils.decorators import retry
from ..strategies.base_strategy import FileHandlingStrategy

logger = logging.getLogger(__name__)

class Watcher(FileSystemEventHandler):
    """Watcher for monitoring file system changes."""

    def __init__(self, watch_folder: str, destination_folder: str, file_types: Optional[List[str]] = None, 
                 strategy: FileHandlingStrategy = None, operation: str = "move"):
        """
        Initialize the file system watcher.

        :param watch_folder: Folder to watch for changes
        :param destination_folder: Where to move/copy the files
        :param file_types: List of allowed file extensions (e.g., [".jpg", ".png"])
        :param strategy: The file handling strategy (Photo, Generic, etc.)
        :param operation: Either "move" or "copy" (defaults to "move")
        """
        self.watch_folder = watch_folder
        self.destination_folder = destination_folder
        self.file_types = file_types if file_types else []
        self.strategy = strategy
        self.operation = operation

    @retry
    def handle_file(self, event):
        """Handle file processing with retry logic in case of failures."""
        if event.is_directory:
            return
    
        # Check if the file type matches the configured list
        if self.file_types and not any(event.src_path.endswith(ext) for ext in self.file_types):
            return
        
        try:
            # Use the strategy to construct the destination path
            dest_path = self.strategy.build_destination_path(event.src_path, self.destination_folder)
            
            # Ensure the destination folder exists
            FileHandler.ensure_directory_exists(os.path.dirname(dest_path))
            
            # Dynamically select and execute the correct operation
            self.strategy.execute_operation(self.operation, event.src_path, dest_path)
        
        except Exception as e:
            logger.error(f"❌ Error processing file {event.src_path}: {e}")
            raise  # Rethrow exception so retry can trigger

    def on_created(self, event):
        """Handle newly created files and apply retry logic."""
        self.handle_file(event)