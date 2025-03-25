import time
import logging
import shutil
import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from .base_strategy import FileHandlingStrategy
from ..factories.strategy_factory import StrategyFactory

logger = logging.getLogger(__name__)

@StrategyFactory.register("photo")
class PhotoFileHandlingStrategy(FileHandlingStrategy):
    """Strategy for handling photo files."""

    def build_destination_path(self, src_path: str, destination_folder: str) -> str:
        """Construct the destination path for the photo file."""
        try:
            # Extract year, month name, and filename from EXIF metadata
            year, month_name, filename = self._parse_file_path(src_path)
            
            # Get the correct month number from the filename
            month_num = datetime.strptime(month_name, "%b").strftime("%m")  # Convert 'Mar' to '03'

            # Pass all required arguments
            dest_path = self._build_folder_structure(destination_folder, str(year), month_num, month_name, filename)

            return dest_path
        except Exception as e:
            logger.error(f"❌ Error constructing destination path for {src_path}: {e}")
            raise

    def move_file(self, src: str, dst: str) -> None:
        """Move a photo file to the destination."""
        try:
            shutil.move(src, dst)
            logger.info(f"✅ Moved photo: {src} ➡ {dst}")
        except Exception as e:
            logger.error(f"❌ Error moving photo file: {e}")

    def _parse_file_path(self, file_path: str) -> tuple:
        """Parse the file path to extract year, month, and filename from EXIF metadata."""
        try:
            with Image.open(file_path) as image:
                exif_data = image._getexif()

                if exif_data is not None:
                    datetime_original = exif_data.get(36867)  # DateTimeOriginal tag
                    if datetime_original:
                        datetime_obj = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
                        year = datetime_obj.year
                        month_name = datetime_obj.strftime("%b")  # e.g., "Mar"
                        filename = os.path.basename(file_path)
                        return year, month_name, filename
                    else:
                        raise ValueError(f"No DateTimeOriginal tag found in EXIF data for {file_path}.")
                else:
                    raise ValueError(f"No EXIF data found for photo: {file_path}")

        except Exception as e:
            logger.error(f"❌ Error parsing EXIF data for photo {file_path}: {e}")
            raise

    def _build_folder_structure(self, destination_folder: str, year: str, month_num: str, month_name: str, filename: str) -> str:
        """Builds the correct folder structure for storing the photo."""
        try:
            # Create folder path: YYYY/MM MM YYYY/
            dest_folder = os.path.join(destination_folder, year, f"{month_num} {month_name} {year}")
            
            # Ensure final filename format: YYYY MM DD original_filename
            day = filename[6:8]  # Extracting the day from filename
            new_filename = f"{year} {month_num} {day} {filename}"
            
            # Complete destination path
            dest_path = os.path.join(dest_folder, new_filename)

            logger.info(f"Destination path: {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"❌ Error constructing folder structure: {e}")
            raise