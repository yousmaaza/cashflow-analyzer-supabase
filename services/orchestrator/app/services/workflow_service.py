import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import (
    Workflow,
    WorkflowState,
    WorkflowBase,
    DocumentProcessingResult,
    TransactionAnalysisResult
)
from .document_client import DocumentProcessorClient
from .transaction_client import TransactionAnalyzerClient
from .supabase_client import SupabaseClient

class WorkflowService:
    def __init__(self, config: ServiceConfig):
        """Initialize workflow service

        Args:
            config: Service configuration
        """
        self.config = config
        self.document_client = DocumentProcessorClient(config)
        self.transaction_client = TransactionAnalyzerClient(config)
        self.storage_client = SupabaseClient(config)

    async def start_workflow(self, workflow_data: WorkflowBase) -> Workflow:
        """Start a new workflow

        Args:
            workflow_data: Initial workflow data

        Returns:
            Created workflow
        """
        # Create new workflow
        workflow = Workflow(
            id=str(uuid4()),
            user_id=workflow_data.user_id,
            document_path=workflow_data.document_path,
            state=WorkflowState.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to Supabase
        await self.storage_client.create_workflow(workflow)
        log.info(f"Created workflow {workflow.id} for user {workflow_data.user_id}")

        # Start processing asynchronously
        asyncio.create_task(self._execute_workflow(workflow))

        return workflow

    async def _execute_workflow(self, workflow: Workflow) -> None:
        """Execute workflow steps

        Args:
            workflow: Workflow to execute
        """
        try:
            # 1. Document Processing
            await self._process_document(workflow)
            if workflow.state == WorkflowState.FAILED:
                return

            # 2. Transaction Analysis
            await self._analyze_transactions(workflow)
            if workflow.state == WorkflowState.FAILED:
                return

            # 3. Final Storage
            await self._store_final_results(workflow)

            # Mark as completed
            workflow.state = WorkflowState.COMPLETED
            workflow.updated_at = datetime.utcnow()
            await self.storage_client.update_workflow(workflow)
            log.info(f"Workflow {workflow.id} completed successfully")

        except Exception as e:
            await self._handle_workflow_error(workflow, str(e))

    async def _process_document(self, workflow: Workflow) -> None:
        """Process document step

        Args:
            workflow: Current workflow
        """
        try:
            workflow.state = WorkflowState.DOCUMENT_PROCESSING
            await self.storage_client.update_workflow(workflow)
            log.info(f"Processing document for workflow {workflow.id}")

            result = await self.document_client.process_document(workflow.document_path)
            
            if result.error:
                raise Exception(f"Document processing failed: {result.error}")

            workflow.results['document_processing'] = result.dict()
            log.info(f"Document processing completed for workflow {workflow.id}")

        except Exception as e:
            await self._handle_workflow_error(workflow, f"Document processing error: {str(e)}")
            raise

    async def _analyze_transactions(self, workflow: Workflow) -> None:
        """Analyze transactions step

        Args:
            workflow: Current workflow
        """
        try:
            workflow.state = WorkflowState.TRANSACTION_ANALYSIS
            await self.storage_client.update_workflow(workflow)
            log.info(f"Analyzing transactions for workflow {workflow.id}")

            doc_result = workflow.results.get('document_processing', {})
            transactions = doc_result.get('transactions', [])

            # Process in batches
            batches = self._create_transaction_batches(transactions)
            results = await self.transaction_client.batch_analyze_transactions(
                workflow.user_id, 
                batches
            )

            # Aggregate results
            all_transactions = []
            total_time = 0
            errors = []

            for result in results:
                if result.error:
                    errors.append(result.error)
                all_transactions.extend(result.transactions)
                total_time += result.processing_time

            if errors:
                raise Exception(f"Transaction analysis errors: {', '.join(errors)}")

            workflow.results['transaction_analysis'] = {
                'transactions': all_transactions,
                'processing_time': total_time
            }
            log.info(f"Transaction analysis completed for workflow {workflow.id}")

        except Exception as e:
            await self._handle_workflow_error(workflow, f"Transaction analysis error: {str(e)}")
            raise

    async def _store_final_results(self, workflow: Workflow) -> None:
        """Store final results step

        Args:
            workflow: Current workflow
        """
        try:
            workflow.state = WorkflowState.STORAGE
            await self.storage_client.update_workflow(workflow)
            log.info(f"Storing final results for workflow {workflow.id}")

            analysis_results = workflow.results.get('transaction_analysis', {})
            transactions = analysis_results.get('transactions', [])

            await self.storage_client.store_transactions(
                workflow.user_id,
                transactions
            )
            log.info(f"Final results stored for workflow {workflow.id}")

        except Exception as e:
            await self._handle_workflow_error(workflow, f"Storage error: {str(e)}")
            raise

    def _create_transaction_batches(self, transactions: List[Dict]) -> List[List[Dict]]:
        """Split transactions into batches

        Args:
            transactions: List of transactions

        Returns:
            List of transaction batches
        """
        batch_size = self.config.workflow.batch_size
        return [transactions[i:i + batch_size] for i in range(0, len(transactions), batch_size)]

    async def _handle_workflow_error(self, workflow: Workflow, error: str) -> None:
        """Handle workflow error

        Args:
            workflow: Current workflow
            error: Error message
        """
        log.error(f"Error in workflow {workflow.id}: {error}")
        workflow.state = WorkflowState.FAILED
        workflow.error = error
        workflow.updated_at = datetime.utcnow()
        await self.storage_client.update_workflow(workflow)

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow if found, None otherwise
        """
        return await self.storage_client.get_workflow(workflow_id)

    async def get_user_workflows(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Workflow]:
        """Get workflows for a user

        Args:
            user_id: User ID
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip

        Returns:
            List of workflows
        """
        return await self.storage_client.get_user_workflows(user_id, limit, offset)

    async def retry_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retry a failed workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow if found and retried, None otherwise
        """
        workflow = await self.get_workflow(workflow_id)
        if not workflow or workflow.state != WorkflowState.FAILED:
            return None

        if workflow.retries >= self.config.workflow.max_retries:
            return None

        workflow.state = WorkflowState.PENDING
        workflow.error = None
        workflow.retries += 1
        workflow.last_retry_at = datetime.utcnow()
        workflow.updated_at = datetime.utcnow()

        await self.storage_client.update_workflow(workflow)
        asyncio.create_task(self._execute_workflow(workflow))

        return workflow