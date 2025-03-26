from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)

def retry(func: callable) -> callable:
    """Retries a function up to MAX_RETRIES times with exponential backoff."""
    def wrapper(self, *args, **kwargs):
        max_retries = 3
        backoff_multiplier = 5

        for attempt in range(max_retries):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                time.sleep(backoff_multiplier ** attempt)
        logger.error(f"❌ Operation failed after {max_retries} attempts.")
    
    return wrapper