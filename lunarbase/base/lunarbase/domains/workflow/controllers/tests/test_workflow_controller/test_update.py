#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestUpdate:
    def test_updates_workflow(self, controller, mock_workflow_search_index, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        controller.save(workflow, user_id)

        updated_workflow = WorkflowModel(   
            name="Updated Workflow",
            description="Updated workflow",
            id=workflow.id,
        )

        resulted_workflow = controller.update(updated_workflow, user_id)

        mock_workflow_search_index.remove_document.assert_called_once_with(workflow.id, user_id)

        assert resulted_workflow.id == updated_workflow.id
        assert resulted_workflow.name == updated_workflow.name
        assert resulted_workflow.description == updated_workflow.description 