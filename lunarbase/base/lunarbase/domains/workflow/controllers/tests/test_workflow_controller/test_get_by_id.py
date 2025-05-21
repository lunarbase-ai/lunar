#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestGetById:
    def test_gets_workflow_by_id(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        controller.save(workflow, user_id)

        resulted_workflow = controller.get_by_id(workflow.id, user_id)

        assert resulted_workflow.id == workflow.id
        assert resulted_workflow.name == workflow.name
        assert resulted_workflow.description == workflow.description 