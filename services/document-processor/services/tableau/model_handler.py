import torch
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import numpy as np
from typing import List
from .models import TableBox
from .config import TableConfig

class ModelHandler:
    def __init__(self, config: TableConfig):
        self.config = config
        self.model = self._load_model()

    def _load_model(self) -> YOLO:
        """Load and configure YOLO model"""
        model_path = hf_hub_download(
            repo_id=self.config.model_repo_id,
            filename=self.config.model_filename
        )
        model = YOLO(model_path)

        if hasattr(model, 'to'):
            model = model.to(self.config.device)

        return model

    def detect_tables(self, image: np.ndarray) -> List[TableBox]:
        """Detect tables in image using YOLO model

        Args:
            image: Input image

        Returns:
            List of detected table boxes
        """
        try:
            results = self.model(image)
            if len(results) > 0:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                return [TableBox.from_coordinates(box) for box in boxes]
            return []
        except Exception as e:
            print(f"Error detecting tables: {e}")
            return []