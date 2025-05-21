#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import pytest

class TestSave:
    def test_saves_workflow(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),  
        )
        saved_workflow = controller.save(workflow, user_id)
        assert saved_workflow.id == workflow.id
        assert saved_workflow.name == workflow.name
        assert saved_workflow.description == workflow.description

    def test_saves_default_workflow_if_none_provided(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        saved_workflow = controller.save(None, user_id)
        assert saved_workflow.id is not None
        assert saved_workflow.name == "Untitled"
        assert saved_workflow.description == ""

    def test_initializes_workflow_dirs(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),  
        )
        controller.save(workflow, user_id)

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