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

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        assert path.exists()

class TestDeleteWorkflow:
    def test_deletes_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description", 
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow)

        path = workflow_repository._get_user_workflow_path(workflow.id, user_id)

        assert Path(path).exists()

        workflow_repository.delete(user_id, workflow.id)

        assert not Path(path).exists()

class TestTmpDeleteWorkflow:
    def test_tmp_deletes_workflow(self, workflow_repository, config):

        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        workflow_repository.tmp_save(user_id, workflow)

        assert path.exists()

        workflow_repository.tmp_delete(user_id, workflow.id)
        assert not path.exists()

class TestUpdateWorkflow:
    def test_updates_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        workflow = workflow_repository.save(user_id, workflow)

        assert workflow.name == "Workflow Name"

        workflow.name = "Updated Workflow Name"

        workflow = workflow_repository.update(user_id, workflow)

        assert workflow.name == "Updated Workflow Name"

class TestShowWorkflow:
    def test_shows_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow)

        shown_workflow = workflow_repository.show(user_id, workflow.id)

        assert shown_workflow.id == workflow.id

class TestIndexWorkflows:
    def test_get_all_workflows(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow)

        workflow2 = WorkflowModel(
            name="Workflow Name 2",
            description="Workflow Description 2",
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow2)

        workflows = workflow_repository.index(user_id)

        assert len(workflows) == 2
        assert workflow in workflows
        assert workflow2 in workflows

    def test_get_all_workflows_without_user_id(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        workflow_repository.save(user_id, workflow)

        workflows = workflow_repository.index()

        assert len(workflows) > 1
        assert workflow in workflows
