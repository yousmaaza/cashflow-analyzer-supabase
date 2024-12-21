from pathlib import Path
import torch

class TableConfig:
    def __init__(self):
        self.temp_dir = Path("temp")
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        
        # Configuration par défaut du modèle
        self.model_repo_id = "keremberke/yolov8m-table-extraction"
        self.model_filename = "best.pt"
        
        # Création des dossiers nécessaires
        self.temp_dir.mkdir(exist_ok=True)

    @property
    def temp_image_path(self) -> Path:
        return self.temp_dir / "temp_table.jpg"