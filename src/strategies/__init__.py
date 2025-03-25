from pathlib import Path
import pkgutil
import importlib
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

directory = Path(__file__).parent

for _, module_name, _ in pkgutil.iter_modules([str(directory)]):
    try:
        full_module_name = f"{__name__}.{module_name}"
        logger.debug(f"📂 Importing module: {full_module_name}")
        importlib.import_module(full_module_name)
    except Exception as e:
        logger.error(f"❌ Failed to import {full_module_name}: {e}")