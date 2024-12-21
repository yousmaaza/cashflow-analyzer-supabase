from pathlib import Path
from typing import List, Any
from ..core.config import ServiceConfig
from .ocr.extractor import OcrExtractor
from .tableau.extractor import TableauExtractor

class DocumentProcessor:
    def __init__(self, config_path: Path = None):
        """Initialize document processor

        Args:
            config_path: Optional path to config file
        """
        self.config = ServiceConfig(config_path)
        self.ocr_extractor = OcrExtractor(self.config)
        self.tableau_extractor = TableauExtractor(self.config)

    def process_document(self, pdf_path: Path) -> Any:
        """Process a PDF document"""
        if not self.config.validate_file(pdf_path):
            raise ValueError(f"Invalid file: {pdf_path}")

        # Process document
        try:
            self.config.create_directories()
            # ... reste du traitement ...
        finally:
            self.config.cleanup()