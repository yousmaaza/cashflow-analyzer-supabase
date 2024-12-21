import numpy as np
from typing import List, Dict, Optional
from .models import Word, Line, BoundingBox
from core.config import ServiceConfig
from .image_processor import ImageProcessor
from .word_processor import WordProcessor
from .line_processor import LineProcessor

class OcrExtractor:
    def __init__(self, ocr_model, config: Optional[ServiceConfig] = None):
        """Initialize OCR Extractor

        Args:
            ocr_model: Pretrained OCR model from doctr
            config: Configuration object for OCR parameters
        """
        self.ocr_model = ocr_model
        self.config = config or ServiceConfig()
        self.word_processor = WordProcessor(self.config)
        self.line_processor = LineProcessor(self.config)

    def extract_text_from_region(self, image: np.ndarray, box: List[float]) -> List[Dict]:
        """Extract and process text from image region

        Args:
            image: Input image
            box: Region coordinates [x1, y1, x2, y2]

        Returns:
            List of processed lines with word information
        """
        # Prepare image
        ImageProcessor.prepare_region(image, box, self.config.ocr.temp_path)

        # Extract words
        doc = ImageProcessor.get_document(self.config.ocr.temp_path)
        result = self.ocr_model(doc)
        
        # Process words
        words = self._extract_words(result, box)
        debit_x = self.word_processor.find_debit_column(words)
        words = self.word_processor.process_debit_amounts(words, debit_x)
        
        # Group into lines
        lines = self.line_processor.process_lines(words)
        
        return [self._line_to_dict(line) for line in lines]

    def _extract_words(self, doc_result, box: List[float]) -> List[Word]:
        """Extract words from OCR result"""
        x1, y1, x2, y2 = map(int, box)
        words = []

        for page in doc_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        bbox = self._create_bbox(word.geometry, x1, y1, x2, y2)
                        words.append(Word(
                            text=word.value,
                            confidence=word.confidence,
                            bbox=bbox
                        ))
        return words

    def _create_bbox(self, geometry, x1, y1, x2, y2):
        return BoundingBox(
            x1=x1 + int(geometry[0][0] * (x2 - x1)),
            y1=y1 + int(geometry[0][1] * (y2 - y1)),
            x2=x1 + int(geometry[1][0] * (x2 - x1)),
            y2=y1 + int(geometry[1][1] * (y2 - y1))
        )

    def _line_to_dict(self, line: Line) -> Dict:
        """Convert Line object to dictionary"""
        return {
            'words': [{
                'text': word.text,
                'confidence': word.confidence,
                'bbox': vars(word.bbox),
                'x_center': word.x_center,
                'y_center': word.y_center
            } for word in line.words],
            'y_position': line.y_position
        }