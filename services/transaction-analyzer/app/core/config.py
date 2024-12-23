from typing import Optional

import yaml
from pathlib import Path

class ServiceConfig:
    def __init__(self, config_path: Optional[Path] = None):

        # Default path is relative to the service root
        service_root = Path(__file__).parent.parent
        self.config_path = config_path or service_root / "config" / "config.yaml"
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from YAML file"""
        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)

    def create_directories(self):
        """Create necessary directories based on configuration"""
        output_folders = self.config.get("output_folders", {})
        for folder in output_folders.values():
            Path(folder).mkdir(parents=True, exist_ok=True)

    def get_llm_config(self) -> dict:
        """Get LLM configuration"""
        return self.config.get("llm", {})

    def get_categorization_config(self) -> dict:
        """Get categorization configuration"""
        return self.config.get("categorization", {})

    def get_api_config(self) -> dict:
        """Get API configuration"""
        return self.config.get("api", {})

    def get_database_config(self) -> dict:
        """Get database configuration"""
        return self.config.get("database", {})

