from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import os


@dataclass
class ServiceEndpoints:
    """Configuration des endpoints de services"""
    process: str = "/process"
    analyze: str = "/analyze"
    health: str = "/health"


@dataclass
class ServiceConfig:
    """
    Configuration centralisée du service d'orchestration
    """
    workflow: Dict[str, Any] = field(default_factory=lambda: {
        'max_retries': 3,
        'retry_delay': 60,
        'batch_size': 50,
        'timeout': 300
    })

    output_folders: Dict[str, str] = field(default_factory=lambda: {
        'workflows': 'output/workflows',
        'logs': 'output/logs',
        'temp': 'output/temp',
        'cache': 'output/cache'
    })

    services: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'document_processor': {
            'url': os.getenv('DOCUMENT_PROCESSOR_URL', 'http://localhost:8000'),
            'endpoints': {
                'process': '/process',
                'health': '/health'
            }
        },
        'transaction_analyzer': {
            'url': os.getenv('TRANSACTION_ANALYZER_URL', 'http://localhost:8001'),
            'endpoints': {
                'analyze': '/analyze',
                'health': '/health'
            }
        }
    })

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialise la configuration du service

        Args:
            config_path: Chemin optionnel vers le fichier de configuration
        """
        # Chemin par défaut du fichier de configuration
        service_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or service_root / "config" / "config.yaml"

        # Charger la configuration
        self._load_config()

    def _load_config(self):
        """Charge la configuration à partir du fichier YAML"""
        try:
            # Charger le fichier de configuration
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Workflow Configuration
            self.workflow.update(config.get('workflow', {}))

            # Output Folders Configuration
            self.output_folders.update(config.get('output_folders', {}))

            # Services Configuration
            services_config = config.get('services', {})
            for service_name in ['document_processor', 'transaction_analyzer']:
                if service_name in services_config:
                    self.services[service_name].update(services_config[service_name])

        except Exception as e:
            print(f"Erreur de chargement de la configuration : {e}")

    def create_directories(self):
        """Crée les répertoires nécessaires"""
        for folder in self.output_folders.values():
            Path(folder).mkdir(parents=True, exist_ok=True)

    @property
    def document_processor_url(self) -> str:
        """URL du service de traitement de documents"""
        return self.services['document_processor']['url']

    @property
    def transaction_analyzer_url(self) -> str:
        """URL du service d'analyse de transactions"""
        return self.services['transaction_analyzer']['url']

    def get_service_endpoint(self, service_name: str, endpoint_name: str) -> str:
        """
        Récupère l'URL complète d'un endpoint de service

        Args:
            service_name: Nom du service ('document_processor' ou 'transaction_analyzer')
            endpoint_name: Nom de l'endpoint

        Returns:
            URL complète de l'endpoint
        """
        service = self.services.get(service_name, {})
        url = service.get('url', '')
        endpoints = service.get('endpoints', {})
        endpoint = endpoints.get(endpoint_name, '')
        return f"{url}{endpoint}"