import pytest
from lunarbase.domains.workflow.repositories import LocalFilesWorkflowRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import uuid

@pytest.fixture
def connection(config):
    return LocalFilesStorageConnection(config)

@pytest.fixture
def workflow_repository(config, connection):
    return LocalFilesWorkflowRepository(
        config=config,
        connection=connection
    )

class TestSaveWorkflow:
    def test_saves_workflow_returns_saved_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        saved_workflow = workflow_repository.save(user_id, workflow)

        assert saved_workflow.id == workflow.id

    def test_saves_workflow_in_correct_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
    
        workflow_repository.save(user_id, workflow)

        path = workflow_repository._get_user_workflow_path(workflow.id, user_id)
        
        assert Path(path).exists()

    def test_saves_default_workflow_if_none_provided(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        saved_workflow = workflow_repository.save(user_id)

        assert saved_workflow.name == "Untitled"
        assert saved_workflow.description == ""

class TestTmpSaveWorkflow:
    def test_tmp_saves_workflow_returns_saved_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        saved_workflow = workflow_repository.tmp_save(user_id, workflow)

        assert saved_workflow.id == workflow.id
        
    def test_tmp_saves_workflow_in_correct_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        workflow_repository.tmp_save(user_id, workflow)

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, workflow.id, f"{workflow.id}.json")

        assert path.exists()

class TestPathBuilding:
    def test_gets_user_workflows_root_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        expected_path = str(Path(config.USER_DATA_PATH, user_id, config.USER_WORKFLOW_ROOT))

        assert workflow_repository._get_user_workflows_root_path(user_id) == expected_path

    def test_gets_user_workflow_venv_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow_id = str(uuid.uuid4())

        workflow_root_path = workflow_repository._get_user_workflows_root_path(user_id)

        expected_path = str(Path(workflow_root_path, workflow_id, config.USER_WORKFLOW_VENV_ROOT))

        assert workflow_repository._get_user_workflow_venv_path(workflow_id, user_id) == expected_path

    def test_gets_user_workflows_index_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        expected_path = str(Path(config.USER_DATA_PATH, user_id, config.USER_INDEX_ROOT, config.WORKFLOW_INDEX_NAME))

        assert workflow_repository._get_user_workflows_index_path(user_id) == expected_path

    def test_gets_user_workflow_reports_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow_id = str(uuid.uuid4())

        workflow_root_path = workflow_repository._get_user_workflows_root_path(user_id)

        expected_path = str(Path(workflow_root_path, workflow_id, config.REPORT_PATH))

        assert workflow_repository._get_user_workflow_reports_path(user_id, workflow_id) == expected_path
    
    def test_gets_user_workflow_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow_id = str(uuid.uuid4())

        workflow_root_path = workflow_repository._get_user_workflows_root_path(user_id)

        expected_path = str(Path(workflow_root_path, workflow_id))

        assert workflow_repository._get_user_workflow_path(workflow_id, user_id) == expected_path

    def test_gets_user_workflow_files_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow_id = str(uuid.uuid4())

        workflow_root_path = workflow_repository._get_user_workflows_root_path(user_id)

        expected_path = str(Path(workflow_root_path, workflow_id, config.FILES_PATH))

        assert workflow_repository._get_user_workflow_files_path(user_id, workflow_id) == expected_path
