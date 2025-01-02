import os
from pathlib import Path
from typing import Dict, Any, Optional

from zenml.config.global_config import GlobalConfiguration
from zenml.config.pipeline_configurations import PipelineConfiguration


class ZenMLConfiguration:
    """
    Configuration centralisée pour ZenML
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialise la configuration ZenML

        Args:
            config_path: Chemin optionnel vers le fichier de configuration
        """
        # Chemin par défaut
        self.service_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.service_root / "config" / "zenml_config.yaml"

        # Configuration globale ZenML
        self.global_config = GlobalConfiguration()

        # Charger la configuration
        self._load_config()

    def _load_config(self):
        """
        Charge la configuration à partir du fichier YAML
        """
        try:
            # Configuration par défaut
            default_config = {
                'tracking': {
                    'experiment_name': 'cashflow_analyzer',
                    'artifact_store_path': str(self.service_root / '.zenml' / 'artifact_store')
                },
                'pipelines': {
                    'cache_enabled': True,
                    'max_cache_size_gb': 5,
                    'debug_mode': False
                }
            }

            # Créer les répertoires nécessaires
            Path(default_config['tracking']['artifact_store_path']).mkdir(parents=True, exist_ok=True)

            # Configuration globale
            self.global_config.set_artifact_store_path(
                default_config['tracking']['artifact_store_path']
            )

        except Exception as e:
            print(f"Erreur de configuration ZenML : {e}")

    def get_pipeline_configuration(self) -> PipelineConfiguration:
        """
        Génère une configuration de pipeline basée sur les paramètres

        Returns:
            Configuration de pipeline ZenML
        """
        return PipelineConfiguration(
            experiment_name='cashflow_analyzer',
            step_cache_enabled=True,
            step_cache_max_size_gb=5
        )

    def get_pipeline_settings(self) -> Dict[str, Any]:
        """
        Récupère les paramètres des pipelines

        Returns:
            Dictionnaire de configuration des pipelines
        """
        return {
            "cache_enabled": True,
            "max_cache_size_gb": 5,
            "debug_mode": False
        }


# Instance globale de configuration
zenml_config = ZenMLConfiguration()