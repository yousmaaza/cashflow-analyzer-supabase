import cv2
import numpy as np
from typing import List
from .models import TableBox

class TableVisualizer:
    def __init__(self):
        self.colors = [
            (255, 0, 0),    # Rouge
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (255, 255, 0),  # Jaune
            (255, 0, 255)   # Magenta
        ]

    def draw_detections(self, image: np.ndarray, boxes: List[TableBox]) -> np.ndarray:
        """Visualize detected tables on image

        Args:
            image: Input image
            boxes: List of detected table boxes

        Returns:
            Image with visualized detections
        """
        img_copy = image.copy()

        for idx, box in enumerate(boxes):
            color = self.colors[idx % len(self.colors)]
            cv2.rectangle(
                img_copy,
                (box.x1, box.y1),
                (box.x2, box.y2),
                color,
                2
            )
            
            # Ajouter un label
            cv2.putText(
                img_copy,
                f"Table {idx+1}",
                (box.x1, box.y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

        return img_copy