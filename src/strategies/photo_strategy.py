import os
import logging
from typing import Optional, Callable, Dict
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from .base_strategy import FileHandlingStrategy
from ..factories.strategy_factory import StrategyFactory
from ..utils.decorators import retry

logger = logging.getLogger(__name__)

@StrategyFactory.register("photo")
class PhotoFileHandlingStrategy(FileHandlingStrategy):
    """Strategy for handling photo and video files based on metadata."""

    def __init__(self):
        self.metadata_extractors: Dict[str, Callable[[str], Optional[tuple]]] = {
            ".jpg": self._extract_exif_data,
            ".jpeg": self._extract_exif_data,
            ".png": self._extract_exif_data,
            ".mp4": self._extract_video_metadata,
            ".mov": self._extract_video_metadata,
            ".avi": self._extract_video_metadata,
        }

    def build_destination_path(self, src_path: str, destination_folder: str) -> Optional[str]:
        """Construct the destination path for the file."""
        try:
            ext = os.path.splitext(src_path)[1].lower()

            if ext not in self.metadata_extractors:
                logger.warning(f"❌ Unsupported file type: {ext} - {src_path}")
                return None

            metadata_extractor = self.metadata_extractors.get(ext)
            
            if metadata_extractor:
                metadata = metadata_extractor(src_path)

                if metadata:
                    year, month_num, month_name, day_number = metadata
                    filename = os.path.basename(src_path)
                    dest_path = self._build_folder_structure(destination_folder, year, month_num, month_name, day_number, filename)
                    return dest_path
            
            else:
                logger.warning(f"❌ No metadata extractor found for file type: {ext} - {src_path}")
                return None

        except Exception as e:
            logger.error(f"❌ Error constructing destination path for {src_path}: {e}")
            return None

    @retry
    def _extract_exif_data(self, file_path: str) -> Optional[tuple]:
        """Extract EXIF metadata from an image file."""
        try:
            with Image.open(file_path) as image:
                exif_data = image._getexif()
                if exif_data:
                    return self._parse_exif_metadata(exif_data)
        except Exception as e:
            logger.warning(f"❌ Error extracting EXIF metadata from {file_path}: {e}")
            return None
    
    @retry
    def _extract_video_metadata(self, file_path: str) -> Optional[tuple]:
        """Extract metadata from a video file."""
        try:
            parser = createParser(file_path)
            if not parser:
                logger.warning(f"Failed to parse video file: {file_path}")
                return None
            
            metadata = extractMetadata(parser)
            if metadata and metadata.has("creation_date"):
                datetime_obj = metadata.getValues("creation_date")[0]
                year = str(datetime_obj.year)
                month_num = datetime_obj.strftime("%m")
                month_name = datetime_obj.strftime("%b")
                day_number = datetime_obj.strftime("%d")
                return year, month_num, month_name, day_number
        except Exception as e:
            logger.warning(f"❌ Error extracting metadata from video {file_path}: {e}")
            return None

    def _parse_exif_metadata(self, exif_data: dict) -> Optional[tuple]:
        """Helper method to parse the EXIF metadata and extract date-related information."""
        try:
            datetime_original = exif_data.get(36867)  # DateTimeOriginal tag
            if datetime_original:
                datetime_obj = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
                year = str(datetime_obj.year)
                month_num = datetime_obj.strftime("%m")
                month_name = datetime_obj.strftime("%b")
                day_number = datetime_obj.strftime("%d")
                return year, month_num, month_name, day_number
        except Exception as e:
            logger.warning(f"❌ Error parsing EXIF data: {e}")
        return None

    def _build_folder_structure(self, destination_folder: str, year: str, month_num: str, month_name: str, day_number: str, filename: str) -> str:
        """Builds the correct folder structure for storing the file."""
        try:
            dest_folder = os.path.join(destination_folder, year, f"{month_num} {month_name} {year}")
            filename_date_prefix = f"{year} {month_num} {day_number}"
            new_filename = f"{filename_date_prefix} {filename}"
            dest_path = os.path.join(dest_folder, new_filename)
            logger.info(f"Destination path: {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"❌ Error constructing folder structure for {filename}: {e}")
            return None
