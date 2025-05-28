#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestAutoModify:
    def test_auto_modify_uses_agent_copilot(self, controller, mock_agent_copilot, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",  
            id=str(uuid.uuid4()),
        )
        intent = "Modify the workflow"
        modified_workflow = controller.auto_modify(workflow, intent, user_id)

        mock_agent_copilot.modify_workflow.assert_called_once_with(workflow, intent)

        assert modified_workflow.name == mock_agent_copilot.modify_workflow.return_value.name
        assert modified_workflow.description == mock_agent_copilot.modify_workflow.return_value.description
        assert modified_workflow.id == mock_agent_copilot.modify_workflow.return_value.id 