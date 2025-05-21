#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import pytest

class TestTmpSave:
    def test_returns_temporary_saved_workflow(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        saved_workflow = controller.tmp_save(workflow, user_id)
        assert saved_workflow.id == workflow.id
        assert saved_workflow.name == workflow.name
        assert saved_workflow.description == workflow.description

    def test_saves_workflow_in_tmp_path(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        controller.tmp_save(workflow, user_id)

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        assert path.exists() 