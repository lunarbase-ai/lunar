#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import WorkflowModel

class TestListAll:
    def test_lists_all_workflows(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )

        workflow2 = WorkflowModel(
            name="Test Workflow 2",
            description="A test workflow 2",
            id=str(uuid.uuid4()),
        )
        controller.save(workflow, user_id)
        controller.save(workflow2, user_id)

        workflows = controller.list_all(user_id)
        assert len(workflows) == 2

        result_ids = [w.id for w in workflows]
        assert workflow.id in result_ids
        assert workflow2.id in result_ids 