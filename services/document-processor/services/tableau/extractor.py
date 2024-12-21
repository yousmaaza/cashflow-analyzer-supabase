from typing import List, Any
from pathlib import Path
import numpy as np
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from ...core.config import ServiceConfig

class TableauExtractor:
    def __init__(self, config: ServiceConfig):
        """Initialize Tableau Extractor

        Args:
            config: Service configuration
        """
        self.config = config.tableau
        self.model = self._load_model()

    def _load_model(self) -> YOLO:
        """Load and configure YOLO model"""
        model_path = hf_hub_download(
            repo_id=self.config.model_repo_id,
            filename=self.config.model_filename
        )
        return YOLO(model_path).to(self.config.torch_device)

    def detect_tables(self, image: np.ndarray) -> List[List[float]]:
        """Detect tables in image"""
        results = self.model(image)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        return boxes.tolist()