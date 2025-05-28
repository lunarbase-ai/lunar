#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestUpdateWorkflow:
    def test_updates_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        workflow = workflow_repository.save(user_id, workflow)

        assert workflow.name == "Workflow Name"

        workflow.name = "Updated Workflow Name"

        workflow = workflow_repository.update(user_id, workflow)

        assert workflow.name == "Updated Workflow Name" 