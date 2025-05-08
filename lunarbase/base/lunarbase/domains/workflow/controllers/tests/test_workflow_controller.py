import uuid
from lunarbase.modeling.data_models import WorkflowModel
import pytest
import os
from pathlib import Path

class TestTmpSave:
    def test_tmp_save_returns_saved_workflow(self, workflow_controller, config):
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
    

    def test_tmp_save_creates_file_in_tmp_path(self, workflow_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        workflow_controller.tmp_save(workflow, user_id)

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        assert path.exists()
