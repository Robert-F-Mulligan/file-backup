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

    def __init__(self, watch_folder: str, destination_folder: str, file_types: Optional[List[str]] = None, strategy: FileHandlingStrategy = None):
        self.watch_folder = watch_folder
        self.destination_folder = destination_folder
        self.file_types = file_types if file_types else []
        self.strategy = strategy

    @retry
    def handle_file(self, event):
        """Handle the file processing with retries in case of failures."""
        if event.is_directory:
            return
    
        # Check if the file type matches
        if self.file_types and not any(event.src_path.endswith(ext) for ext in self.file_types):
            return
        
        try:
            # Use the strategy to construct the destination path
            dest_path = self.strategy.build_destination_path(event.src_path, self.destination_folder)
            
            # Ensure the destination folder exists
            FileHandler.ensure_directory_exists(os.path.dirname(dest_path))
            
            # Move the file
            self.strategy.move_file(event.src_path, dest_path)
        
        except Exception as e:
            logger.error(f"❌ Error processing file {event.src_path}: {e}")
            raise  # Rethrow exception so retry can trigger
    def on_created(self, event):
        """Handle newly created files and apply retry logic."""
        self.handle_file(event)