import os
import pytest
from pathlib import Path
from unittest.mock import Mock

from app.core.config import ServiceConfig
from app.services.document_client import DocumentProcessorClient
from app.services.transaction_client import TransactionAnalyzerClient
from app.services.supabase_client import SupabaseClient
from app.services.workflow_service import WorkflowService

@pytest.fixture
def test_config():
    """Create test configuration"""
    # Override config path for testing
    config_path = Path(__file__).parent / 'test_config.yaml'
    return ServiceConfig(config_path=config_path)

@pytest.fixture
def mock_document_client(test_config):
    """Create mock document processor client"""
    client = Mock(spec=DocumentProcessorClient)
    client.config = test_config
    return client

@pytest.fixture
def mock_transaction_client(test_config):
    """Create mock transaction analyzer client"""
    client = Mock(spec=TransactionAnalyzerClient)
    client.config = test_config
    return client

@pytest.fixture
def mock_supabase_client(test_config):
    """Create mock Supabase client"""
    client = Mock(spec=SupabaseClient)
    client.config = test_config
    return client

@pytest.fixture
def workflow_service(test_config, mock_document_client, mock_transaction_client, mock_supabase_client):
    """Create workflow service with mock clients"""
    service = WorkflowService(test_config)
    service.document_client = mock_document_client
    service.transaction_client = mock_transaction_client
    service.storage = mock_supabase_client
    return service