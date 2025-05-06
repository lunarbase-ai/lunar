import pytest
from lunarbase.domains.workflow.repositories import LocalFilesWorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from pathlib import Path

@pytest.fixture
def connection(config):
    return LocalFilesStorageConnection(config)

@pytest.fixture
def workflow_repository(config, connection):
    return LocalFilesWorkflowRepository(
        config=config,
        connection=connection
    )

def test_builds_user_workflows_root_path(workflow_repository, config):
    user_id = "user_id"
    expected_path = str(Path(config.USER_DATA_PATH, user_id, config.USER_WORKFLOW_ROOT))

    assert workflow_repository._build_user_workflows_root_path(user_id) == expected_path

def test_builds_user_workflow_venv_path(workflow_repository, config):
    user_id = "user_id"
    workflow_id = "workflow_id"

    workflow_root_path = workflow_repository._build_user_workflows_root_path(user_id)

    expected_path = str(Path(workflow_root_path, workflow_id, config.USER_WORKFLOW_VENV_ROOT))

    assert workflow_repository._build_user_workflow_venv_path(workflow_id, user_id) == expected_path

def test_builds_user_workflows_index_path(workflow_repository, config):
    user_id = "user_id"
    expected_path = str(Path(config.USER_DATA_PATH, user_id, config.USER_INDEX_ROOT, config.WORKFLOW_INDEX_NAME))

    assert workflow_repository._build_user_workflows_index_path(user_id) == expected_path

def test_builds_user_workflow_reports_path(workflow_repository, config):
    user_id = "user_id"
    workflow_id = "workflow_id"

    workflow_root_path = workflow_repository._build_user_workflows_root_path(user_id)

    expected_path = str(Path(workflow_root_path, workflow_id, config.REPORT_PATH))

    assert workflow_repository._build_user_workflow_reports_path(user_id, workflow_id) == expected_path