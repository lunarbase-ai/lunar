#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
from pathlib import Path
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestDelete:
    def test_deletes_workflow(self, controller, config, mock_workflow_search_index):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        controller.save(workflow, user_id)

        workflow_path = Path(config.USER_DATA_PATH, user_id, config.USER_WORKFLOW_ROOT, workflow.id, f"{workflow.id}.json")

        assert workflow_path.exists()

        result = controller.delete(workflow.id, user_id)
        mock_workflow_search_index.remove_document.assert_called_once_with(workflow.id, user_id)

        assert result
        assert not workflow_path.exists() 