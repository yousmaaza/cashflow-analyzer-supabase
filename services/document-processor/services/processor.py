import time
from pathlib import Path
from typing import List

from .models import ProcessedDocument, Transaction
from .config import ServiceConfig
from .ocr.extractor import OcrExtractor
from .tableau.extractor import TableauExtractor

class DocumentProcessor:
    def __init__(self, config_path: Path = None):
        """Initialize document processor with configuration

        Args:
            config_path: Optional path to config file
        """
        self.config = ServiceConfig(config_path)
        self.config.create_directories()

        # Initialize extractors with configurations
        self.tableau_extractor = TableauExtractor(self.config.tableau)
        self.ocr_extractor = OcrExtractor(self.config.ocr)

    def process_document(self, pdf_path: Path) -> ProcessedDocument:
        """Process a PDF document to extract transactions

        Args:
            pdf_path: Path to PDF file

        Returns:
            ProcessedDocument with extracted transactions
        """
        start_time = time.time()
        
        try:
            # Validate file
            if not self.config.validate_file(pdf_path):
                raise ValueError(f"Invalid file: {pdf_path}")

            # Process document
            images = self.tableau_extractor.convert_pdf_to_image(pdf_path)
            transactions = []

            for idx, image in enumerate(images):
                page_transactions = self.process_page(image, idx)
                transactions.extend(page_transactions)

            document = ProcessedDocument(
                transactions=transactions,
                page_count=len(images),
                filename=pdf_path.name,
                processing_time=time.time() - start_time
            )

            # Cleanup temporary files
            self.config.cleanup()

            return document

        except Exception as e:
            self.config.cleanup()
            return ProcessedDocument(
                transactions=[],
                page_count=0,
                filename=pdf_path.name,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def process_page(self, image: Any, page_num: int) -> List[Transaction]:
        """Process a single page

        Args:
            image: Page image
            page_num: Page number

        Returns:
            List of extracted transactions
        """
        transactions = []

        # Detect and process tables
        table_boxes = self.tableau_extractor.detect_tables(image)
        
        for box in table_boxes:
            lines = self.ocr_extractor.extract_text_from_region(image, box)
            page_transactions = self.process_lines(lines, page_num)
            transactions.extend(page_transactions)

        return transactions