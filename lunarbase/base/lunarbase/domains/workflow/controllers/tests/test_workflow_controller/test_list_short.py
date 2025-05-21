#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestListShort:
    def test_lists_short_workflows(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        controller.save(workflow, user_id)

        workflows = controller.list_short(user_id)

        assert len(workflows) == 1
        assert workflows[0].id == workflow.id
        assert workflows[0].name == workflow.name
        assert workflows[0].description == workflow.description 