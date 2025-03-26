import os
import logging
from typing import Optional
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from .base_strategy import FileHandlingStrategy
from ..factories.strategy_factory import StrategyFactory
from ..utils.file_handler import FileHandler
from ..utils.decorators import retry

logger = logging.getLogger(__name__)

@StrategyFactory.register("photo")
class PhotoFileHandlingStrategy(FileHandlingStrategy):
    """Strategy for handling photo files based on EXIF metadata."""

    def __init__(self, operation: str = "copy"):
        super().__init__(operation)

    def build_destination_path(self, src_path: str, destination_folder: str) -> Optional[str]:
        """Construct the destination path for the photo file."""
        try:
            year, month_num, month_name = self._extract_exif_data(src_path)

            if year == "Unknown":
                logger.warning(f"⚠️ No EXIF date found for {src_path}, using 'Unknown' folder.")

            filename = os.path.basename(src_path)
            dest_path = self._build_folder_structure(destination_folder, year, month_num, month_name, filename)

            if dest_path:
                # Perform the file operation (move or copy)
                FileHandler.execute_operation(self.operation, src_path, dest_path)

            return dest_path

        except Exception as e:
            logger.error(f"❌ Error constructing destination path for {src_path}: {e}")

    def _parse_exif_metadata(self, exif_data: dict) -> tuple:
        """Helper method to parse the EXIF metadata and extract date-related information."""
        try:
            # Extract DateTimeOriginal if available
            datetime_original = exif_data.get(36867)  # DateTimeOriginal tag
            if datetime_original:
                datetime_obj = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
                year = str(datetime_obj.year)
                month_num = datetime_obj.strftime("%m")  # "03"
                month_name = datetime_obj.strftime("%b")  # "Mar"
                return year, month_num, month_name

        except Exception as e:
            logger.warning(f"❌ Error parsing EXIF data: {e}")

        # Fallback values if no EXIF data is found or error occurs
        return "Unknown", "00", "Unknown"

    @retry  # Apply the retry decorator here
    def _extract_exif_data(self, file_path: str) -> tuple:
        """Extract EXIF metadata from the image file."""
        try:
            with Image.open(file_path) as image:
                exif_data = image._getexif()
                
                if exif_data:
                    return self._parse_exif_metadata(exif_data)

        except PermissionError as e:
            logger.warning(f"❌ Permission denied when accessing {file_path}: {e}")
            raise e  # Re-raise so retry can handle it
            
        except Exception as e:
            logger.warning(f"❌ Error extracting EXIF metadata from {file_path}: {e}")

        # Fallback values if no EXIF data is found or error occurs
        return "Unknown", "00", "Unknown"

    def _build_folder_structure(self, destination_folder: str, year: str, month_num: str, month_name: str, filename: str) -> str:
        """Builds the correct folder structure for storing the photo."""
        try:
            # Create folder path: YYYY/MM MM YYYY/
            dest_folder = os.path.join(destination_folder, year, f"{month_num} {month_name} {year}")

            # Ensure filename format: YYYY MM DD original_filename
            filename_date_prefix = f"{year} {month_num} {filename[:2]}" if filename[:2].isdigit() else f"{year} {month_num} 01"
            new_filename = f"{filename_date_prefix} {filename}"

            # Complete destination path
            dest_path = os.path.join(dest_folder, new_filename)

            logger.info(f"Destination path: {dest_path}")
            return dest_path

        except Exception as e:
            logger.error(f"❌ Error constructing folder structure for {filename}: {e}")
            return None
