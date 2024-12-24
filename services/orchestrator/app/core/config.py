from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import yaml

@dataclass
class WorkflowConfig:
    max_retries: int
    retry_delay: int
    timeout: int
    batch_size: int

@dataclass
class ServiceEndpoints:
    process: str
    status: str = ""
    analyze: str = ""

@dataclass
class ServiceConfig:
    url: str
    timeout: int
    endpoints: ServiceEndpoints

@dataclass
class ServicesConfig:
    document_processor: ServiceConfig
    transaction_analyzer: ServiceConfig

@dataclass
class DatabaseConfig:
    table_name: str
    max_connections: int
    connection_timeout: int

@dataclass
class ApiConfig:
    batch_timeout: int
    rate_limit: int

@dataclass
class OutputFoldersConfig:
    logs: str
    temp: str

class ServiceConfig:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize service configuration

        Args:
            config_path: Path to YAML configuration file
                        If None, uses default path
        """
        # Default path is relative to the service root
        service_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or service_root / "config" / "config.yaml"
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Initialize Workflow configuration
        self.workflow = WorkflowConfig(
            max_retries=config['workflow']['max_retries'],
            retry_delay=config['workflow']['retry_delay'],
            timeout=config['workflow']['timeout'],
            batch_size=config['workflow']['batch_size']
        )

        # Initialize Services configuration
        self.services = ServicesConfig(
            document_processor=ServiceConfig(
                url=config['services']['document_processor']['url'],
                timeout=config['services']['document_processor']['timeout'],
                endpoints=ServiceEndpoints(
                    process=config['services']['document_processor']['endpoints']['process'],
                    status=config['services']['document_processor']['endpoints']['status']
                )
            ),
            transaction_analyzer=ServiceConfig(
                url=config['services']['transaction_analyzer']['url'],
                timeout=config['services']['transaction_analyzer']['timeout'],
                endpoints=ServiceEndpoints(
                    analyze=config['services']['transaction_analyzer']['endpoints']['analyze']
                )
            )
        )

        # Initialize Database configuration
        self.database = DatabaseConfig(
            table_name=config['database']['table_name'],
            max_connections=config['database']['max_connections'],
            connection_timeout=config['database']['connection_timeout']
        )

        # Initialize API configuration
        self.api = ApiConfig(
            batch_timeout=config['api']['batch_timeout'],
            rate_limit=config['api']['rate_limit']
        )

        # Initialize Output Folders configuration
        self.output_folders = OutputFoldersConfig(
            logs=config['output_folders']['logs'],
            temp=config['output_folders']['temp']
        )

    def create_directories(self) -> None:
        """Create necessary directories"""
        Path(self.output_folders.logs).mkdir(parents=True, exist_ok=True)
        Path(self.output_folders.temp).mkdir(parents=True, exist_ok=True)

    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # Check workflow configuration
            assert self.workflow.max_retries > 0, "max_retries must be positive"
            assert self.workflow.retry_delay > 0, "retry_delay must be positive"
            assert self.workflow.timeout > 0, "timeout must be positive"
            assert self.workflow.batch_size > 0, "batch_size must be positive"

            # Check services URLs
            assert self.services.document_processor.url.startswith(('http://', 'https://'))
            assert self.services.transaction_analyzer.url.startswith(('http://', 'https://'))

            # Check database configuration
            assert self.database.max_connections > 0
            assert self.database.connection_timeout > 0

            # Check API configuration
            assert self.api.batch_timeout > 0
            assert self.api.rate_limit > 0

            return True

        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {str(e)}")

        except Exception as e:
            raise ValueError(f"Unexpected error during configuration validation: {str(e)}")