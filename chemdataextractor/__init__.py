"""Lightweight scientific document loading."""

import logging

from .doc.document import Document

__title__ = "ChemDataExtractor Lite"
__version__ = "1.0.0"
__license__ = "MIT"

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["Document"]
