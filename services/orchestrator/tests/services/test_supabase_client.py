import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from app.models.schemas import Workflow, WorkflowState
from app.services.supabase_client import SupabaseClient

pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def mock_supabase():
    return Mock()

@pytest.fixture
def supabase_client(test_config, mock_supabase):
    with patch('app.services.supabase_client.create_client', return_value=mock_supabase):
        client = SupabaseClient(test_config)
        return client

@pytest.mark.asyncio
async def test_create_workflow(supabase_client, mock_supabase):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.execute = AsyncMock()

    # Act
    await supabase_client.create_workflow(workflow)

    # Assert
    mock_supabase.table.assert_called_once_with('workflows')
    table_mock.insert.assert_called_once()
    table_mock.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_workflow(supabase_client, mock_supabase):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.COMPLETED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.execute = AsyncMock()

    # Act
    await supabase_client.update_workflow(workflow)

    # Assert
    mock_supabase.table.assert_called_once_with('workflows')
    table_mock.update.assert_called_once()
    table_mock.eq.assert_called_once_with('id', workflow.id)
    table_mock.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_workflow_success(supabase_client, mock_supabase):
    # Arrange
    workflow_id = "test-id"
    workflow_data = {
        'id': workflow_id,
        'user_id': 'test-user',
        'document_path': '/test/doc.pdf',
        'state': 'completed',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.execute = AsyncMock(return_value=Mock(data=[workflow_data]))

    # Act
    workflow = await supabase_client.get_workflow(workflow_id)

    # Assert
    assert workflow is not None
    assert workflow.id == workflow_id
    assert workflow.state == WorkflowState.COMPLETED

@pytest.mark.asyncio
async def test_get_workflow_not_found(supabase_client, mock_supabase):
    # Arrange
    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.execute = AsyncMock(return_value=Mock(data=[]))

    # Act
    workflow = await supabase_client.get_workflow("non-existent-id")

    # Assert
    assert workflow is None

@pytest.mark.asyncio
async def test_store_transactions_success(supabase_client, mock_supabase):
    # Arrange
    transactions = [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200}
    ]
    user_id = "test-user"

    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.upsert.return_value = table_mock
    table_mock.execute = AsyncMock()

    # Act
    await supabase_client.store_transactions(user_id, transactions)

    # Assert
    mock_supabase.table.assert_called_with('transactions')
    table_mock.upsert.assert_called_once()
    table_mock.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_workflows(supabase_client, mock_supabase):
    # Arrange
    user_id = "test-user"
    workflow_data = [
        {
            'id': "test-id-1",
            'user_id': user_id,
            'document_path': '/test/doc1.pdf',
            'state': 'completed',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        },
        {
            'id': "test-id-2",
            'user_id': user_id,
            'document_path': '/test/doc2.pdf',
            'state': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    ]

    table_mock = Mock()
    mock_supabase.table.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.offset.return_value = table_mock
    table_mock.execute = AsyncMock(return_value=Mock(data=workflow_data))

    # Act
    workflows = await supabase_client.get_user_workflows(user_id)

    # Assert
    assert len(workflows) == 2
    assert all(w.user_id == user_id for w in workflows)
    assert any(w.state == WorkflowState.COMPLETED for w in workflows)
    assert any(w.state == WorkflowState.PENDING for w in workflows)