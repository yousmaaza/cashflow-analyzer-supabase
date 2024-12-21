from pdf2image import convert_from_path
import numpy as np
from typing import List
import cv2
from pathlib import Path

class PDFProcessor:
    @staticmethod
    def convert_to_images(pdf_path: Path) -> List[np.ndarray]:
        """Convert PDF pages to images

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of images (one per page)
        """
        try:
            # Convert PDF pages to PIL images
            pil_images = convert_from_path(pdf_path)
            
            # Convert PIL images to numpy arrays
            return [PDFProcessor._convert_pil_to_cv2(img) for img in pil_images]
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []

    @staticmethod
    def _convert_pil_to_cv2(pil_image) -> np.ndarray:
        """Convert PIL image to OpenCV format"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)