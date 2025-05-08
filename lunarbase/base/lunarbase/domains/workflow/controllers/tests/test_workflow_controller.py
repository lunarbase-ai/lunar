import uuid
from lunarbase.modeling.data_models import WorkflowModel
import pytest
import os
from pathlib import Path

class TestTmpSave:
    def test_returns_temporary_saved_workflow(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        saved_workflow = workflow_controller.tmp_save(workflow, user_id)
        assert saved_workflow.id == workflow.id
        assert saved_workflow.name == workflow.name
        assert saved_workflow.description == workflow.description
    

    def test_saves_workflow_in_tmp_path(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        workflow_controller.tmp_save(workflow, user_id)

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        assert path.exists()

class TestTmpDelete:
    def test_deletes_temporary_saved_workflow(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")
        workflow_controller.tmp_save(workflow, user_id)

        assert path.exists()

        assert workflow_controller.tmp_delete(workflow.id, user_id)

        assert not path.exists()

class TestSave:
    def test_saves_workflow(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),  
        )
        saved_workflow = workflow_controller.save(workflow, user_id)
        assert saved_workflow.id == workflow.id
        assert saved_workflow.name == workflow.name
        assert saved_workflow.description == workflow.description

    def test_saves_default_workflow_if_none_provided(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        saved_workflow = workflow_controller.save(None, user_id)
        assert saved_workflow.id is not None
        assert saved_workflow.name == "Untitled"
        assert saved_workflow.description == ""

    def test_initializes_workflow_dirs(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),  
        )
        workflow_controller.save(workflow, user_id)

        workflow_root_path = Path(
            config.USER_DATA_PATH,
            user_id,
            config.USER_WORKFLOW_ROOT,
            workflow.id,
        )
        workflow_venv_path = Path(
            workflow_root_path,
            config.USER_WORKFLOW_VENV_ROOT,
        )
        workflow_files_path = Path(
            workflow_root_path,
            config.FILES_PATH,
        )
        workflow_reports_path = Path(
            workflow_root_path,
            config.REPORT_PATH,
        )
        assert workflow_root_path.exists()
        assert workflow_venv_path.exists()
        assert workflow_files_path.exists()
        assert workflow_reports_path.exists()