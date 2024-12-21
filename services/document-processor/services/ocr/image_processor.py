import cv2
import numpy as np
from doctr.io import DocumentFile
from pathlib import Path
from typing import List, Tuple

class ImageProcessor:
    @staticmethod
    def prepare_region(image: np.ndarray, box: List[float], temp_path: Path) -> np.ndarray:
        """Prepare and save image region for OCR

        Args:
            image: Input image
            box: Region coordinates [x1, y1, x2, y2]
            temp_path: Path to save temporary image

        Returns:
            Prepared image region
        """
        x1, y1, x2, y2 = map(int, box)
        region = image[y1:y2, x1:x2]
        cv2.imwrite(
            str(temp_path),
            cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        )
        return region

    @staticmethod
    def get_document(temp_path: Path) -> DocumentFile:
        """Create DocumentFile from image"""
        return DocumentFile.from_images(str(temp_path))