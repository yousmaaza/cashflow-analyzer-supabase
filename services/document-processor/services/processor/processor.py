import time
from typing import Any, Dict, List
from pathlib import Path

from .models import ProcessedDocument, Transaction
from .config import ProcessorConfig
from .transaction_extractor import TransactionExtractor
from .validator import TransactionValidator
from .categorizer import TransactionCategorizer

class DocumentProcessor:
    def __init__(self, tableau_extractor: Any, ocr_extractor: Any, config: ProcessorConfig = None):
        """Initialize document processor

        Args:
            tableau_extractor: Table detection service
            ocr_extractor: OCR service
            config: Processor configuration
        """
        self.tableau_extractor = tableau_extractor
        self.ocr_extractor = ocr_extractor
        self.config = config or ProcessorConfig()
        
        # Initialize components
        self.extractor = TransactionExtractor(self.config)
        self.validator = TransactionValidator(self.config)
        self.categorizer = TransactionCategorizer(self.config)

    def process_document(self, pdf_path: Path) -> ProcessedDocument:
        """Process a PDF document to extract transactions

        Args:
            pdf_path: Path to PDF file

        Returns:
            ProcessedDocument with extracted transactions
        """
        start_time = time.time()
        
        try:
            # Extract tables from document
            images = self.tableau_extractor.convert_pdf_to_image()
            transactions = []

            for idx, image in enumerate(images):
                page_transactions = self.process_page(image, idx)
                transactions.extend(page_transactions)

            # Post-process transactions
            valid_transactions = self.validator.validate_transactions(transactions)
            categorized_transactions = self.categorizer.categorize_transactions(valid_transactions)

            return ProcessedDocument(
                transactions=categorized_transactions,
                page_count=len(images),
                filename=pdf_path.name,
                processing_time=time.time() - start_time
            )

        except Exception as e:
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
        # Detect tables
        table_boxes = self.tableau_extractor.detect_tables(image)
        page_transactions = []

        for box in table_boxes:
            # Extract text from table
            lines = self.ocr_extractor.extract_text_from_region(image, box)
            
            # Extract transactions from text
            transactions = self.extractor.extract_transactions(lines, page_num)
            page_transactions.extend(transactions)

        return page_transactions