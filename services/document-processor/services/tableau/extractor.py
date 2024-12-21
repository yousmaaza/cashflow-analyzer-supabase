from pathlib import Path
import numpy as np
from typing import List, Optional
from .config import TableConfig
from .models import TableBox, ProcessedTable
from .pdf_processor import PDFProcessor
from .model_handler import ModelHandler
from .visualizer import TableVisualizer

class TableauExtractor:
    def __init__(self, config: Optional[TableConfig] = None):
        """Initialize TableauExtractor

        Args:
            config: Configuration object for table extraction
        """
        self.config = config or TableConfig()
        self.model_handler = ModelHandler(self.config)
        self.visualizer = TableVisualizer()

    def process_document(self, pdf_path: Path) -> List[List[ProcessedTable]]:
        """Process entire PDF document

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of processed tables per page
        """
        images = PDFProcessor.convert_to_images(pdf_path)
        return [self.process_page(image, page_num) for page_num, image in enumerate(images)]

    def process_page(self, image: np.ndarray, page_num: int) -> List[ProcessedTable]:
        """Process a single page

        Args:
            image: Page image
            page_num: Page number

        Returns:
            List of processed tables from the page
        """
        tables = []
        detected_boxes = self.model_handler.detect_tables(image)

        for box in detected_boxes:
            table_image = box.extract_region(image)
            tables.append(ProcessedTable(
                image=table_image,
                coordinates=box,
                page_number=page_num
            ))

        return tables

    def visualize_detections(self, image: np.ndarray, boxes: List[TableBox]) -> np.ndarray:
        """Visualize detected tables

        Args:
            image: Input image
            boxes: Detected table boxes

        Returns:
            Image with visualized detections
        """
        return self.visualizer.draw_detections(image, boxes)