import time
import logging
import os
from .base_strategy import FileHandlingStrategy
from ..factories.strategy_factory import StrategyFactory


@StrategyFactory.register("default")
class GenericFileHandlingStrategy(FileHandlingStrategy):
    """Strategy for handling non-photo files (e.g., documents)."""

    def build_destination_path(self, src_path: str, destination_folder: str) -> str:
        """Simply copy the file and preserve folder structure."""
        try:
            # We don't need to parse EXIF for generic files, so just get the filename
            filename = os.path.basename(src_path)
            # Use the helper function to preserve the folder structure
            dest_path = build_folder_structure(destination_folder, filename=filename)

            return dest_path

        except Exception as e:
            logger.error(f"❌ Error constructing destination path for generic file: {e}")
            raise