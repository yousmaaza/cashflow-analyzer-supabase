from typing import Dict, Any, List
from zenml import pipeline, step
import pandas as pd

from app.core.config import ServiceConfig
from app.core.logger import log
from app.clients.document_processor_client import DocumentProcessorClient
from app.clients.transaction_analyzer_client import TransactionAnalyzerClient
from app.orchestration.zenml_config import zenml_config


class WorkflowOrchestrator:
    """
    Classe d'orchestration des workflows financiers utilisant ZenML
    """

    def __init__(self, config: ServiceConfig):
        """
        Initialise l'orchestrateur

        Args:
            config: Configuration du service
        """
        self.config = config
        self.document_client = DocumentProcessorClient(config)
        self.transaction_client = TransactionAnalyzerClient(config)

        # Récupérer la configuration du pipeline
        self.pipeline_config = zenml_config.get_pipeline_configuration()

    @step(enable_cache=True)
    def extract_document_data(self, document_path: str) -> Dict[str, Any]:
        """
        Étape d'extraction des données du document

        Args:
            document_path: Chemin du document à traiter

        Returns:
            Métadonnées et données extraites
        """
        try:
            log.info(f"Extraction des données du document : {document_path}")
            result = self.document_client.process_document(document_path)

            # Tracking manuel des métriques
            from zenml.steps import StepContext
            step_context = StepContext.get_active_context()
            step_context.log_metrics({
                "document_pages": result.get('page_count', 0),
                "document_processing_time": result.get('processing_time', 0)
            })

            return result
        except Exception as e:
            log.error(f"Erreur d'extraction : {e}")
            raise

    @step(enable_cache=True)
    def preprocess_transactions(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prétraitement des transactions

        Args:
            document_data: Données extraites du document

        Returns:
            Liste de transactions prétraitées
        """
        try:
            transactions = document_data.get('transactions', [])

            preprocessed = []
            for tx in transactions:
                preprocessed_tx = {
                    **tx,
                    'description': tx['description'].upper().strip(),
                    'amount': float(tx.get('amount', 0))
                }
                preprocessed.append(preprocessed_tx)

            # Tracking manuel des métriques
            from zenml.steps import StepContext
            step_context = StepContext.get_active_context()
            step_context.log_metrics({
                "transactions_count": len(preprocessed),
                "unique_descriptions": len(set(tx['description'] for tx in preprocessed))
            })

            log.info(f"Prétraitement de {len(preprocessed)} transactions")
            return preprocessed
        except Exception as e:
            log.error(f"Erreur de prétraitement : {e}")
            raise

    @step
    def categorize_transactions(
            self,
            user_id: str,
            transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Catégorisation des transactions

        Args:
            user_id: Identifiant de l'utilisateur
            transactions: Liste des transactions à catégoriser

        Returns:
            Résultats de l'analyse
        """
        try:
            log.info(f"Catégorisation de {len(transactions)} transactions")
            analysis_result = self.transaction_client.analyze_transactions(
                user_id,
                transactions
            )

            # Tracking manuel des métriques
            from zenml.steps import StepContext
            step_context = StepContext.get_active_context()
            step_context.log_metrics({
                "categories_count": len(set(
                    tx.get('category', 'Uncategorized')
                    for tx in analysis_result.get('transactions', [])
                ))
            })

            return analysis_result
        except Exception as e:
            log.error(f"Erreur de catégorisation : {e}")
            raise

    @step
    def aggregate_financial_insights(
            self,
            categorized_transactions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Agrégation des insights financiers

        Args:
            categorized_transactions: Transactions catégorisées

        Returns:
            Insights financiers
        """
        try:
            transactions = categorized_transactions.get('transactions', [])

            # Conversion en DataFrame pour analyse
            df = pd.DataFrame(transactions)

            # Agrégations par catégorie
            category_totals = df.groupby('category')['amount'].agg(['sum', 'count'])

            # Calculs d'insights
            insights = {
                'total_spending': df[df['amount'] < 0]['amount'].sum(),
                'total_income': df[df['amount'] > 0]['amount'].sum(),
                'category_breakdown': category_totals.to_dict(),
                'top_categories': category_totals['sum'].nlargest(3).to_dict()
            }

            # Tracking manuel des métriques
            from zenml.steps import StepContext
            step_context = StepContext.get_active_context()
            step_context.log_metrics({
                "total_spending": insights['total_spending'],
                "total_income": insights['total_income'],
                "top_categories_count": len(insights['top_categories'])
            })

            log.info("Génération des insights financiers")
            return insights
        except Exception as e:
            log.error(f"Erreur de génération des insights : {e}")
            raise

    @pipeline(enable_cache=True)
    def run_financial_workflow(
            self,
            user_id: str,
            document_path: str
    ) -> Dict[str, Any]:
        """
        Pipeline complet du workflow financier

        Args:
            user_id: Identifiant de l'utilisateur
            document_path: Chemin du document

        Returns:
            Résultats complets du workflow
        """
        # 1. Extraction des données du document
        document_data = self.extract_document_data(document_path)

        # 2. Prétraitement des transactions
        preprocessed_transactions = self.preprocess_transactions(document_data)

        # 3. Catégorisation des transactions
        categorized_transactions = self.categorize_transactions(
            user_id,
            preprocessed_transactions
        )

        # 4. Génération des insights
        financial_insights = self.aggregate_financial_insights(
            categorized_transactions
        )

        return {
            'document_data': document_data,
            'transactions': preprocessed_transactions,
            'categorization': categorized_transactions,
            'insights': financial_insights
        }

    def execute_workflow(self, user_id: str, document_path: str):
        """
        Méthode d'exécution du workflow

        Args:
            user_id: Identifiant de l'utilisateur
            document_path: Chemin du document

        Returns:
            Résultats du workflow
        """
        # Initialisation du pipeline avec configuration
        workflow_pipeline = self.run_financial_workflow(user_id, document_path)

        return workflow_pipeline