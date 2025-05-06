import pytest
from lunarbase.domains.workflow.repositories import LocalFilesWorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection


@pytest.fixture
def connection():
    return LocalFilesStorageConnection()

@pytest.fixture
def workflow_repository(config, connection):
    return LocalFilesWorkflowRepository(
        config=config,
        connection=connection
    )

def test_teste(workflow_repository):
    assert workflow_repository.teste() == 'teste'