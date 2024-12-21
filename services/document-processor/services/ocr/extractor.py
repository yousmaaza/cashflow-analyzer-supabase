from typing import List, Dict, Any
from pathlib import Path
import cv2
import numpy as np
from doctr.io import DocumentFile
from ...core.config import ServiceConfig

class OcrExtractor:
    def __init__(self, config: ServiceConfig):
        """Initialize OCR Extractor

        Args:
            config: Service configuration
        """
        self.config = config.ocr
        self.config.temp_path.mkdir(parents=True, exist_ok=True)

    def extract_text_from_region(self, image: np.ndarray, box: List[float]) -> List[Dict]:
        """Extract text from image region"""
        region = self._prepare_region(image, box)
        words = self._process_region(region)
        return self._group_words(words)

    def _prepare_region(self, image: np.ndarray, box: List[float]) -> np.ndarray:
        x1, y1, x2, y2 = map(int, box)
        region = image[y1:y2, x1:x2]
        cv2.imwrite(
            str(self.config.temp_path / "temp_region.jpg"), 
            cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        )
        return region