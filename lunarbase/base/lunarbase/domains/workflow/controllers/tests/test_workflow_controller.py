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

