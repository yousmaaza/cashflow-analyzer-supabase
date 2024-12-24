from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import Workflow, WorkflowState

class SupabaseClient:
    def __init__(self, config: ServiceConfig):
        """Initialize Supabase client

        Args:
            config: Service configuration
        """
        self.config = config
        self.client: Client = create_client(
            supabase_url=config.supabase.url,
            supabase_key=config.supabase.key
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_workflow(self, workflow: Workflow) -> None:
        """Create a new workflow

        Args:
            workflow: Workflow to create
        """
        try:
            data = self._workflow_to_dict(workflow)
            self.client.table('workflows').insert(data).execute()
            log.info(f"Created workflow {workflow.id} in Supabase")

        except Exception as e:
            log.error(f"Error creating workflow in Supabase: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def update_workflow(self, workflow: Workflow) -> None:
        """Update a workflow

        Args:
            workflow: Workflow to update
        """
        try:
            data = self._workflow_to_dict(workflow)
            data['updated_at'] = datetime.utcnow().isoformat()
            
            self.client.table('workflows')\
                .update(data)\
                .eq('id', workflow.id)\
                .execute()
                
            log.info(f"Updated workflow {workflow.id} in Supabase")

        except Exception as e:
            log.error(f"Error updating workflow in Supabase: {str(e)}")
            raise

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow if found, None otherwise
        """
        try:
            response = self.client.table('workflows')\
                .select('*')\
                .eq('id', workflow_id)\
                .execute()

            if not response.data:
                return None

            return self._dict_to_workflow(response.data[0])

        except Exception as e:
            log.error(f"Error getting workflow from Supabase: {str(e)}")
            return None

    async def get_user_workflows(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Workflow]:
        """Get workflows for a user

        Args:
            user_id: User ID
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip

        Returns:
            List of workflows
        """
        try:
            response = self.client.table('workflows')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()

            return [self._dict_to_workflow(item) for item in response.data]

        except Exception as e:
            log.error(f"Error getting user workflows from Supabase: {str(e)}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def store_transactions(
        self,
        user_id: str,
        transactions: List[Dict]
    ) -> None:
        """Store analyzed transactions

        Args:
            user_id: User ID
            transactions: List of transactions to store
        """
        try:
            # Prepare transactions for storage
            transaction_data = [
                {
                    **transaction,
                    'user_id': user_id,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                for transaction in transactions
            ]

            # Store in batches
            batch_size = 100
            for i in range(0, len(transaction_data), batch_size):
                batch = transaction_data[i:i + batch_size]
                self.client.table('transactions').upsert(batch).execute()

            log.info(f"Stored {len(transactions)} transactions for user {user_id}")

        except Exception as e:
            log.error(f"Error storing transactions in Supabase: {str(e)}")
            raise

    def _workflow_to_dict(self, workflow: Workflow) -> Dict:
        """Convert workflow to dictionary

        Args:
            workflow: Workflow to convert

        Returns:
            Dictionary representation of workflow
        """
        return {
            'id': workflow.id,
            'user_id': workflow.user_id,
            'document_path': workflow.document_path,
            'state': workflow.state.value,
            'error': workflow.error,
            'results': workflow.results,
            'retries': workflow.retries,
            'last_retry_at': workflow.last_retry_at.isoformat() if workflow.last_retry_at else None,
            'created_at': workflow.created_at.isoformat(),
            'updated_at': workflow.updated_at.isoformat()
        }

    def _dict_to_workflow(self, data: Dict) -> Workflow:
        """Convert dictionary to workflow

        Args:
            data: Dictionary to convert

        Returns:
            Workflow object
        """
        return Workflow(
            id=data['id'],
            user_id=data['user_id'],
            document_path=data['document_path'],
            state=WorkflowState(data['state']),
            error=data.get('error'),
            results=data.get('results', {}),
            retries=data.get('retries', 0),
            last_retry_at=datetime.fromisoformat(data['last_retry_at']) if data.get('last_retry_at') else None,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )