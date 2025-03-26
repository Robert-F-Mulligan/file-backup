import os
import logging
from typing import Optional, List
from watchdog.events import FileSystemEventHandler
from ..utils.decorators import retry
from ..strategies.base_strategy import FileHandlingStrategy

logger = logging.getLogger(__name__)

class Watcher(FileSystemEventHandler):
    """Watcher for monitoring file system changes."""

    def __init__(self, watch_folder: str, destination_folder: str, file_types: Optional[List[str]] = None, 
                 strategy: FileHandlingStrategy = None, operation: str = "copy"):
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
        self.processed_files = set()

    @retry
    def handle_file(self, event):
        """Handle file processing with retry logic in case of failures."""
        if event.is_directory:
            return
    
        # Check if the file type matches the configured list
        if self.file_types and not any(event.src_path.endswith(ext) for ext in self.file_types):
            return

        logger.info(f"Handling file: {event.src_path}") 
        
        try:
            dest_path = self.strategy.build_destination_path(event.src_path, self.destination_folder)

            if event.src_path in self.processed_files:
                logger.info(f"File {event.src_path} has already been processed.")
                return
            
            logger.debug(f"Applying {self.operation}: {event.src_path} to {dest_path}")
            self.strategy.execute_operation(self.operation, event.src_path, dest_path)
            self.processed_files.add(event.src_path)
        
        except Exception as e:
            logger.error(f"❌ Error processing file {event.src_path}: {e}")
            raise

    def on_created(self, event):
        """Handle newly created files and apply retry logic."""
        self.handle_file(event)