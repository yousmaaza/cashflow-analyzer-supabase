import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from app.models.schemas import (
    Workflow,
    WorkflowState,
    WorkflowBase,
    DocumentProcessingResult,
    TransactionAnalysisResult
)

pytest_plugins = ['pytest_asyncio']

@pytest.mark.asyncio
async def test_start_workflow(workflow_service):
    # Arrange
    workflow_data = WorkflowBase(
        user_id="test_user",
        document_path="/test/document.pdf"
    )
    workflow_service.storage.create_workflow = AsyncMock()

    # Act
    workflow = await workflow_service.start_workflow(workflow_data)

    # Assert
    assert workflow.user_id == workflow_data.user_id
    assert workflow.document_path == workflow_data.document_path
    assert workflow.state == WorkflowState.PENDING
    workflow_service.storage.create_workflow.assert_called_once()

@pytest.mark.asyncio
async def test_process_document_success(workflow_service):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    doc_result = DocumentProcessingResult(
        page_count=2,
        processing_time=1.5,
        transactions=[{"id": 1}, {"id": 2}]
    )

    workflow_service.document_client.process_document = AsyncMock(return_value=doc_result)
    workflow_service.storage.update_workflow = AsyncMock()

    # Act
    await workflow_service._process_document(workflow)

    # Assert
    assert workflow.state == WorkflowState.DOCUMENT_PROCESSING
    assert workflow.results['document_processing'] == doc_result.dict()
    workflow_service.document_client.process_document.assert_called_once_with(workflow.document_path)

@pytest.mark.asyncio
async def test_analyze_transactions_success(workflow_service):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.DOCUMENT_PROCESSING,
        results={
            'document_processing': {
                'transactions': [{"id": 1}, {"id": 2}]
            }
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    analysis_result = TransactionAnalysisResult(
        processing_time=0.5,
        transactions=[{"id": 1, "category": "expense"}, {"id": 2, "category": "income"}]
    )

    workflow_service.transaction_client.batch_analyze_transactions = AsyncMock(
        return_value=[analysis_result]
    )
    workflow_service.storage.update_workflow = AsyncMock()

    # Act
    await workflow_service._analyze_transactions(workflow)

    # Assert
    assert workflow.state == WorkflowState.TRANSACTION_ANALYSIS
    assert 'transaction_analysis' in workflow.results
    assert len(workflow.results['transaction_analysis']['transactions']) == 2
    workflow_service.transaction_client.batch_analyze_transactions.assert_called_once()

@pytest.mark.asyncio
async def test_handle_workflow_error(workflow_service):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    error_message = "Test error"
    workflow_service.storage.update_workflow = AsyncMock()

    # Act
    await workflow_service._handle_workflow_error(workflow, error_message)

    # Assert
    assert workflow.state == WorkflowState.FAILED
    assert workflow.error == error_message
    workflow_service.storage.update_workflow.assert_called_once_with(workflow)

@pytest.mark.asyncio
async def test_retry_workflow_success(workflow_service):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.FAILED,
        error="Previous error",
        retries=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    workflow_service.get_workflow = AsyncMock(return_value=workflow)
    workflow_service.storage.update_workflow = AsyncMock()

    # Act
    result = await workflow_service.retry_workflow(workflow.id)

    # Assert
    assert result is not None
    assert result.state == WorkflowState.PENDING
    assert result.error is None
    assert result.retries == 1
    workflow_service.storage.update_workflow.assert_called_once()

@pytest.mark.asyncio
async def test_retry_workflow_max_retries_exceeded(workflow_service):
    # Arrange
    workflow = Workflow(
        id="test-id",
        user_id="test-user",
        document_path="/test/doc.pdf",
        state=WorkflowState.FAILED,
        error="Previous error",
        retries=workflow_service.config.workflow.max_retries,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    workflow_service.get_workflow = AsyncMock(return_value=workflow)

    # Act
    result = await workflow_service.retry_workflow(workflow.id)

    # Assert
    assert result is None