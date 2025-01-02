import asyncio
from uuid import uuid4
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import Workflow, WorkflowState
from app.clients.document_processor_client import DocumentProcessorClient
from app.clients.transaction_analyzer_client import TransactionAnalyzerClient


class WorkflowService:
    """
    Service de gestion des workflows d'analyse financière
    """

    def __init__(self, config: Optional[ServiceConfig] = None):
        """
        Initialise le service de workflow

        Args:
            config: Configuration du service
        """
        self.config = config or ServiceConfig()

        # Initialisation des clients de services
        self.document_processor = DocumentProcessorClient(self.config)
        self.transaction_analyzer = TransactionAnalyzerClient(self.config)

        # Liste des workflows en mémoire (à remplacer par un stockage persistant)
        self._workflows: Dict[str, Workflow] = {}

    async def execute_workflow(self, user_id: str, document_path: str) -> Workflow:
        """
        Exécute un workflow complet d'analyse de document

        Args:
            user_id: Identifiant de l'utilisateur
            document_path: Chemin du document à traiter

        Returns:
            Workflow mis à jour
        """
        # Créer un nouveau workflow
        workflow = Workflow(
            id=str(uuid4()),
            user_id=user_id,
            document_path=document_path,
            state=WorkflowState.PENDING
        )

        # Stocker le workflow
        self._workflows[workflow.id] = workflow

        try:
            # 1. Traitement du document
            workflow.state = WorkflowState.PROCESSING
            log.info(f"Traitement du document {document_path}")
            document_result = await self.document_processor.process_document(document_path)

            # 2. Extraction des transactions
            transactions = document_result.get('transactions', [])

            # 3. Analyse des transactions
            workflow.state = WorkflowState.ANALYZING
            log.info(f"Analyse des transactions pour l'utilisateur {user_id}")
            analysis_result = await self.transaction_analyzer.analyze_transactions(
                user_id,
                transactions
            )

            # 4. Finalisation du workflow
            workflow.state = WorkflowState.COMPLETED
            workflow.analysis_results = analysis_result
            workflow.document_metadata = document_result

            log.info(f"Workflow {workflow.id} terminé avec succès")

            return workflow

        except Exception as e:
            # Gestion des erreurs
            workflow.state = WorkflowState.FAILED
            workflow.error = str(e)
            log.error(f"Échec du workflow {workflow.id}: {e}")

            return workflow
        finally:
            # Mise à jour de la date de fin
            workflow.updated_at = datetime.utcnow()

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Récupère un workflow par son identifiant

        Args:
            workflow_id: Identifiant du workflow

        Returns:
            Workflow si trouvé, None sinon
        """
        return self._workflows.get(workflow_id)

    def list_workflows(
            self,
            user_id: Optional[str] = None,
            status: Optional[str] = None,
            page: int = 1,
            page_size: int = 10
    ) -> List[Workflow]:
        """
        Liste les workflows

        Args:
            user_id: Filtrer par identifiant utilisateur
            status: Filtrer par statut
            page: Numéro de page
            page_size: Nombre de workflows par page

        Returns:
            Liste des workflows filtrés
        """
        # Filtrer les workflows
        filtered_workflows = [
            workflow for workflow in self._workflows.values()
            if (user_id is None or workflow.user_id == user_id) and
               (status is None or workflow.state == status)
        ]

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size

        return filtered_workflows[start:end]

    async def retry_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Relance un workflow ayant échoué

        Args:
            workflow_id: Identifiant du workflow à relancer

        Returns:
            Workflow mis à jour, ou None si impossible
        """
        workflow = self.get_workflow(workflow_id)

        if not workflow or workflow.state != WorkflowState.FAILED:
            log.warning(f"Impossible de relancer le workflow {workflow_id}")
            return None

        # Vérifier le nombre de tentatives
        if workflow.retries >= self.config.workflow.get('max_retries', 3):
            log.warning(f"Nombre maximum de tentatives atteint pour {workflow_id}")
            return None

        # Incrémenter le nombre de tentatives
        workflow.retries += 1

        # Relancer le workflow
        return await self.execute_workflow(
            workflow.user_id,
            workflow.document_path
        )

    async def check_health(self) -> Dict[str, Any]:
        """
        Vérifie la santé des services dépendants

        Returns:
            Statut de santé des services
        """
        try:
            # Vérifier la santé des services
            document_processor_health = await self.document_processor.check_health()
            transaction_analyzer_health = await self.transaction_analyzer.check_health()

            return {
                "healthy": (
                        document_processor_health.get('status') == 'healthy' and
                        transaction_analyzer_health.get('status') == 'healthy'
                ),
                "document_processor": document_processor_health,
                "transaction_analyzer": transaction_analyzer_health
            }

        except Exception as e:
            log.error(f"Erreur lors de la vérification de la santé : {e}")
            return {
                "healthy": False,
                "error": str(e)
            }