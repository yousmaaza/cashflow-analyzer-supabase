import httpx
from typing import Dict, Any, List, Optional

from app.core.config import ServiceConfig
from app.core.logger import log


class TransactionAnalyzerClient:
    """
    Client pour communiquer avec le service d'analyse de transactions
    """

    def __init__(self, config: Optional[ServiceConfig] = None):
        """
        Initialise le client d'analyse de transactions

        Args:
            config: Configuration du service
        """
        self.config = config or ServiceConfig()
        self.base_url = self.config.transaction_analyzer_url
        self.analyze_endpoint = self.config.get_service_endpoint(
            'transaction_analyzer', 'analyze'
        )
        self.health_endpoint = self.config.get_service_endpoint(
            'transaction_analyzer', 'health'
        )
        self.timeout = httpx.Timeout(
            self.config.workflow.get('timeout', 30.0)
        )

    async def analyze_transactions(
            self,
            user_id: str,
            transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyse un lot de transactions

        Args:
            user_id: Identifiant de l'utilisateur
            transactions: Liste des transactions à analyser

        Returns:
            Résultats de l'analyse des transactions

        Raises:
            HTTPError: En cas d'erreur lors de l'appel de l'API
        """
        try:
            log.info(f"Analyse de {len(transactions)} transactions pour l'utilisateur {user_id}")

            # Préparer la payload
            payload = {
                "user_id": user_id,
                "transactions": transactions,
                "preferences": {}  # Peut être étendu pour des préférences spécifiques
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.analyze_endpoint}",
                    json=payload
                )

                # Vérifier la réponse
                response.raise_for_status()
                result = response.json()

            log.info(f"Analyse des transactions terminée pour l'utilisateur {user_id}")
            return result

        except httpx.HTTPStatusError as e:
            log.error(f"Erreur HTTP lors de l'analyse des transactions : {e}")
            raise

        except httpx.RequestError as e:
            log.error(f"Erreur de requête lors de l'analyse des transactions : {e}")
            raise

        except Exception as e:
            log.error(f"Erreur inattendue lors de l'analyse des transactions : {e}")
            raise

    async def check_health(self) -> Dict[str, Any]:
        """
        Vérifie la santé du service d'analyse de transactions

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