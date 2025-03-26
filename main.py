import time
import logging
from src.utils.logging_setup import setup_logging
from src.utils.config_loader import load_config
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

    watchers = []
    for job in jobs:
        watch_folder = job.get("watch_folder")
        destination_folder = job.get("destination_folder")
        file_types = job.get("file_types", [])
        job_name = job.get("job_name", "Unnamed Job")
        strategy_name = job.get("strategy", "default")
        operation = job.get("operation", "copy")
        scan_interval = job.get("scan_interval", 60)  # Default to 60s periodic scan

        if not watch_folder or not destination_folder:
            logger.warning(f"❌ Missing watch_folder or destination_folder in job '{job_name}'. Skipping.")
            continue
        
        strategy_instance = StrategyFactory.create(strategy_name)
        logger.info(f"🔧 Using strategy: {strategy_name}")

        if not strategy_instance:
            logger.warning(f"❌ Strategy {strategy_name} not found in job '{job_name}'. Skipping.")
            continue

        logger.info(f"✅ Starting job: {job_name} - Monitoring {watch_folder}...")

        watcher = Watcher(watch_folder=watch_folder, 
                          destination_folder=destination_folder, 
                          file_types=file_types, 
                          strategy=strategy_instance,
                          operation=operation,
                          scan_interval=scan_interval)

        watcher.start_watching()  # Start real-time watching + periodic scanning
        watchers.append(watcher)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping all watchers...")
        for watcher in watchers:
            watcher.stop_watching()


if __name__ == "__main__":
    main()
