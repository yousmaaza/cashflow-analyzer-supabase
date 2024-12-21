import time
from typing import Any
from pathlib import Path

from .models import ProcessedDocument, Transaction
from core.config import ServiceConfig
from .transaction_extractor import TransactionExtractor
from .validator import TransactionValidator
from core.logger import log

class DocumentProcessor:
    def __init__(self, tableau_extractor: Any, ocr_extractor: Any, config: ServiceConfig = None):
        """Initialize document processor

        Args:
            tableau_extractor: Table detection service
            ocr_extractor: OCR service
            config: Processor configuration
        """
        self.tableau_extractor = tableau_extractor
        self.ocr_extractor = ocr_extractor
        self.config = config or ServiceConfig()

        # Initialize components
        self.extractor = TransactionExtractor(self.config)
        self.validator = TransactionValidator(self.config)

    def process_document(self, pdf_path: Path) -> ProcessedDocument:
        """Process a PDF document to extract transactions

        Args:
            pdf_path: Path to PDF file

        Returns:
            ProcessedDocument with extracted transactions
        """
        start_time = time.time()
        log.log_process_start(pdf_path.name)

        try:
            # Process PDF with table extractor
            document_tables = self.tableau_extractor.process_document(pdf_path)
            transactions = []

            # Process each page's tables
            for page_num, page_tables in enumerate(document_tables):
                for table in page_tables:
                    # Extract text from each table
                    box_coordinates = table.coordinates.to_list()
                    lines = self.ocr_extractor.extract_text_from_region(
                        table.image,
                        box_coordinates
                    )

                    # Extract transactions from text
                    page_transactions = self.extractor.extract_transactions(lines, page_num)
                    transactions.extend(page_transactions)

            # Validate transactions
            valid_transactions = self.validator.validate_transactions(transactions)

            log.log_process_end(pdf_path.name, time.time() - start_time)
            return ProcessedDocument(
                transactions=valid_transactions,
                page_count=len(document_tables),
                filename=pdf_path.name,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            log.log_error(e, context=f"processing document {pdf_path.name}")
            return ProcessedDocument(
                transactions=[],
                page_count=0,
                filename=pdf_path.name,
                processing_time=time.time() - start_time,
                error=str(e)
            )