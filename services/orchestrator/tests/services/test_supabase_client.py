import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.models.schemas import Workflow, WorkflowState
from app.services.supabase_client import SupabaseClient

pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def mock_supabase_response():
    return Mock(data=[
        {
            'id': 'test-id',
            'user_id': 'test-user',
            'document_path': '/test/doc.pdf',
            'state': 'completed',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'error': None,
            'results': {},
            'retries': 0,
            'last_retry_at': None
        }
    ])

@pytest.fixture
def supabase_client(test_config):
    with patch('app.services.supabase_client.create_client') as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        client = SupabaseClient(test_config)
        client.client = mock_client
        return client

@pytest.mark.asyncio
async def test_create_workflow(supabase_client):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute = AsyncMock()

    # Act
    await supabase_client.create_workflow(workflow)

    # Assert
    supabase_client.client.table.assert_called_once_with('workflows')
    mock_table.insert.assert_called_once()
    mock_table.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_workflow(supabase_client):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.COMPLETED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute = AsyncMock()

    # Act
    await supabase_client.update_workflow(workflow)

    # Assert
    supabase_client.client.table.assert_called_once_with('workflows')
    mock_table.update.assert_called_once()
    mock_table.eq.assert_called_once_with('id', workflow.id)
    mock_table.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_workflow_success(supabase_client, mock_supabase_response):
    # Arrange
    workflow_id = "test-id"
    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute = AsyncMock(return_value=mock_supabase_response)

    # Act
    workflow = await supabase_client.get_workflow(workflow_id)

    # Assert
    assert workflow is not None
    assert workflow.id == workflow_id
    assert workflow.state == WorkflowState.COMPLETED
    supabase_client.client.table.assert_called_once_with('workflows')

@pytest.mark.asyncio
async def test_get_workflow_not_found(supabase_client):
    # Arrange
    mock_response = Mock(data=[])
    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute = AsyncMock(return_value=mock_response)

    # Act
    workflow = await supabase_client.get_workflow("non-existent-id")

    # Assert
    assert workflow is None

@pytest.mark.asyncio
async def test_store_transactions_success(supabase_client):
    # Arrange
    user_id = "test-user"
    transactions = [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200}
    ]

    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute = AsyncMock()

    # Act
    await supabase_client.store_transactions(user_id, transactions)

    # Assert
    supabase_client.client.table.assert_called_once_with('transactions')
    mock_table.upsert.assert_called_once()
    mock_table.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_workflows(supabase_client, mock_supabase_response):
    # Arrange
    user_id = "test-user"
    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute = AsyncMock(return_value=mock_supabase_response)

    # Act
    workflows = await supabase_client.get_user_workflows(user_id)

    # Assert
    assert len(workflows) == 1
    assert workflows[0].user_id == user_id
    supabase_client.client.table.assert_called_once_with('workflows')

@pytest.mark.asyncio
async def test_error_handling(supabase_client):
    # Arrange
    mock_table = Mock()
    supabase_client.client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute = AsyncMock(side_effect=Exception("Test error"))

    # Act & Assert
    with pytest.raises(Exception):
        await supabase_client.create_workflow(Mock())
