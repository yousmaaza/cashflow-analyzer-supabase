import httpx
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.config import ServiceConfig
from app.core.logger import log


class DocumentProcessorClient:
    """
    Client pour communiquer avec le service de traitement de documents
    """

    def __init__(self, config: Optional[ServiceConfig] = None):
        """
        Initialise le client de traitement de documents

        Args:
            config: Configuration du service
        """
        self.config = config or ServiceConfig()
        self.base_url = self.config.document_processor_url
        self.process_endpoint = self.config.get_service_endpoint(
            'document_processor', 'process'
        )
        self.health_endpoint = self.config.get_service_endpoint(
            'document_processor', 'health'
        )
        self.timeout = httpx.Timeout(
            self.config.workflow.get('timeout', 30.0)
        )

    async def process_document(self, document_path: str) -> Dict[str, Any]:
        """
        Traite un document via l'API de traitement de documents

        Args:
            document_path: Chemin du document à traiter

        Returns:
            Résultats du traitement du document

        Raises:
            HTTPError: En cas d'erreur lors de l'appel de l'API
        """
        try:
            log.info(f"Traitement du document : {document_path}")

            # Vérifier que le fichier existe
            document_file = Path(document_path)
            if not document_file.exists():
                raise FileNotFoundError(f"Le fichier {document_path} n'existe pas")

            # Préparer la requête multipart
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(document_file, 'rb') as file:
                    files = {'file': (document_file.name, file, 'application/pdf')}
                    response = await client.post(
                        f"{self.base_url}{self.process_endpoint}",
                        files=files
                    )

                # Vérifier la réponse
                response.raise_for_status()
                result = response.json()

            log.info(f"Traitement du document terminé : {document_path}")
            return result

        except httpx.HTTPStatusError as e:
            log.error(f"Erreur HTTP lors du traitement du document : {e}")
            raise

        except httpx.RequestError as e:
            log.error(f"Erreur de requête lors du traitement du document : {e}")
            raise

        except Exception as e:
            log.error(f"Erreur inattendue lors du traitement du document : {e}")
            raise

    async def check_health(self) -> Dict[str, Any]:
        """
        Vérifie la santé du service de traitement de documents

        Returns:
            Statut de santé du service
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.health_endpoint}"
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            log.error(f"Erreur lors de la vérification de la santé du service : {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }