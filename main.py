import os
import shutil
import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from PIL.ExifTags import TAGS
from src.utils.logging_setup import setup_logging
from src.utils.config_loader import load_config
from src.utils.decorators import retry
import src.strategies
from src.strategies.base_strategy import FileHandlingStrategy
from src.factories.strategy_factory import StrategyFactory
from src.watchers.watcher import Watcher

logger = logging.getLogger(__name__)

setup_logging()

def main() -> None:
    """Main function to load config, set up watchers, and start monitoring."""
    # Load config
    config = load_config()

    if not config:
        logger.error("❌ Failed to load configuration. Exiting...")
        return

    jobs = config.get("jobs", [])
    if not jobs:
        logger.error("❌ No jobs found in config file.")
        return

    observers = []
    for job in jobs:
        watch_folder = job.get("watch_folder")
        destination_folder = job.get("destination_folder")
        file_types = job.get("file_types", [])
        job_name = job.get("job_name", "Unnamed Job")
        strategy_name = job.get("strategy", "default")

        if not watch_folder or not destination_folder:
            logger.warning(f"❌ Missing watch_folder or destination_folder in job '{job_name}'. Skipping.")
            continue

        # Get the strategy class dynamically
        strategy_instance = StrategyFactory.create(strategy_name)
        logger.info(f"🔧 Using strategy: {strategy_name}")

        if not strategy_instance:
            logger.warning(f"❌ Strategy {strategy_name} not found in job '{job_name}'. Skipping.")
            continue

        logger.info(f"✅ Starting job: {job_name} - Monitoring {watch_folder}...")

        observer = Observer()
        watcher = Watcher(watch_folder, 
                          destination_folder, 
                          file_types, 
                          strategy_instance)

        observer.schedule(watcher, watch_folder, recursive=True)
        observers.append(observer)
        observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()


if __name__ == "__main__":
    main()