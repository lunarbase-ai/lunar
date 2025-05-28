#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestAutoCreate:
    def test_auto_create_uses_agent_copilot(self, controller, mock_agent_copilot, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        intent = "Create a workflow for data processing"
        workflow = controller.auto_create(intent, user_id)

        mock_agent_copilot.generate_workflow.assert_called_once_with(intent)

        assert workflow.name == mock_agent_copilot.generate_workflow.return_value.name
        assert workflow.description == mock_agent_copilot.generate_workflow.return_value.description
        assert workflow.id == mock_agent_copilot.generate_workflow.return_value.id 