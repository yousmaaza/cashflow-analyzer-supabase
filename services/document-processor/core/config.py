from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import yaml
import torch

@dataclass
class OCRConfig:
    x_tolerance: int
    debit_x_tolerance: int
    y_tolerance: int
    min_confidence: float
    temp_dir: str
    date_formats: List[str]

    @property
    def temp_path(self) -> Path:
        return Path(self.temp_dir)

@dataclass
class TableauConfig:
    model_repo_id: str
    model_filename: str
    device: str

    @property
    def torch_device(self) -> torch.device:
        if self.device == "auto":
            if torch.backends.mps.is_available():
                return torch.device("mps")
            elif torch.cuda.is_available():
                return torch.device("cuda")
            return torch.device("cpu")
        return torch.device(self.device)

@dataclass
class DocumentConfig:
    max_file_size_mb: int
    supported_formats: List[str]
    output_dir: str

    @property
    def max_file_size(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

@dataclass
class ValidationConfig:
    min_transaction_amount: float
    required_fields: List[str]

class ServiceConfig:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize service configuration

        Args:
            config_path: Path to YAML configuration file
                        If None, uses default path
        """
        # Default path is relative to the service root
        service_root = Path(__file__).parent.parent
        self.config_path = config_path or service_root / "config" / "config.yaml"
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Initialize OCR configuration
        self.ocr = OCRConfig(
            x_tolerance=config['ocr']['x_tolerance'],
            debit_x_tolerance=config['ocr']['debit_x_tolerance'],
            y_tolerance=config['ocr']['y_tolerance'],
            min_confidence=config['ocr']['min_confidence'],
            temp_dir=config['ocr']['temp_dir'],
            date_formats=config['ocr']['date_formats']
        )

        # Initialize Tableau configuration
        self.tableau = TableauConfig(
            model_repo_id=config['tableau']['model']['repo_id'],
            model_filename=config['tableau']['model']['filename'],
            device=config['tableau']['model']['device']
        )

        # Initialize Document configuration
        self.document = DocumentConfig(
            max_file_size_mb=config['document']['max_file_size_mb'],
            supported_formats=config['document']['supported_formats'],
            output_dir=config['document']['output_dir']
        )

        # Initialize Validation configuration
        self.validation = ValidationConfig(
            min_transaction_amount=config['validation']['min_transaction_amount'],
            required_fields=config['validation']['required_fields']
        )

    def validate_file(self, file_path: Path) -> bool:
        """Validate if a file can be processed

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if file is valid
        """
        # Vérifier le format du fichier
        if file_path.suffix not in self.document.supported_formats:
            return False

        # Vérifier la taille du fichier
        if file_path.stat().st_size > self.document.max_file_size:
            return False

        return True

    def create_directories(self) -> None:
        """Create necessary directories"""
        Path(self.ocr.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.document.output_dir).mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> None:
        """Cleanup temporary files"""
        import shutil
        shutil.rmtree(self.ocr.temp_dir, ignore_errors=True)