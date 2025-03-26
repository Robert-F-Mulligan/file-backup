import os
import logging
import threading
import time
from typing import Optional, List
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from ..utils.decorators import retry
from ..strategies.base_strategy import FileHandlingStrategy

logger = logging.getLogger(__name__)

class Watcher(FileSystemEventHandler):
    """Watcher for monitoring file system changes and performing periodic scans."""

    def __init__(self, watch_folder: str, destination_folder: str, file_types: Optional[List[str]] = None, 
                 strategy: FileHandlingStrategy = None, operation: str = "copy", scan_interval: int = 60):
        """
        Initialize the file system watcher.

        :param watch_folder: Folder to watch for changes
        :param destination_folder: Where to move/copy the files
        :param file_types: List of allowed file extensions (e.g., [".jpg", ".png"])
        :param strategy: The file handling strategy (Photo, Generic, etc.)
        :param operation: Either "move" or "copy" (defaults to "copy")
        :param scan_interval: Interval (in seconds) for periodic scans
        """
        self.watch_folder = watch_folder
        self.destination_folder = destination_folder
        self.file_types = file_types if file_types else []
        self.strategy = strategy
        self.operation = operation
        self.processed_files = set()  # Stores processed file paths to prevent re-processing
        self.scan_interval = scan_interval
        self.observer = Observer()

    @retry
    def handle_file(self, event: FileSystemEvent):
        """Handle file processing with retry logic in case of failures."""
        if isinstance(event, str):
            # If event is a string (from periodic scan), create a mock event
            event = FileSystemEvent(event)

        if event.is_directory:
            return

        file_path = event.src_path
        if self.file_types and not any(file_path.endswith(ext) for ext in self.file_types):
            return

        logger.info(f"Handling file: {file_path}")

        try:
            dest_path = self.strategy.build_destination_path(file_path, self.destination_folder)

            if not dest_path:
                logger.warning(f"❌ Invalid destination path for file {file_path}. Skipping processing.")
                return 

            if file_path in self.processed_files:
                logger.info(f"File {file_path} has already been processed. Skipping.")
                return

            logger.debug(f"Applying {self.operation}: {file_path} to {dest_path}")
            self.strategy.execute_operation(self.operation, file_path, dest_path)
            self.processed_files.add(file_path)

        except Exception as e:
            logger.error(f"❌ Error processing file {file_path}: {e}")
            raise

    def start_watching(self):
        """Start the file system watcher and periodic scanning in parallel."""
        logger.info("📡 Starting file watcher...")
        self.observer.schedule(self, self.watch_folder, recursive=True)
        self.observer.start()

        # Start the periodic scanning in a separate thread
        scan_thread = threading.Thread(target=self.scan_folder_periodically, daemon=True)
        scan_thread.start()

    def stop_watching(self):
        """Stop the file system watcher."""
        logger.info("🛑 Stopping file watcher...")
        self.observer.stop()
        self.observer.join()

    def on_created(self, event: FileSystemEvent):
        """Handle newly created files and apply retry logic."""
        self.handle_file(event)

    def scan_folder_periodically(self):
        """Periodically scan the watch folder for unprocessed files."""
        while True:
            logger.info("🔍 Running periodic scan...")
            try:
                for root, _, files in os.walk(self.watch_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not self.file_types or any(file.endswith(ext) for ext in self.file_types):
                            if file_path not in self.processed_files:
                                self.handle_file(file_path)  # Now correctly passing a mock event
            except Exception as e:
                logger.error(f"❌ Error during periodic scan: {e}")

            time.sleep(self.scan_interval)  # Wait for the next scan cycle
