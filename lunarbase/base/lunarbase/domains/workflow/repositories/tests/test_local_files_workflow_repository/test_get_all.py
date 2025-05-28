#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestGetAllWorkflows:
    def test_get_all_workflows(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow)

        workflow2 = WorkflowModel(
            name="Workflow Name 2",
            description="Workflow Description 2",
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow2)

        workflows = workflow_repository.get_all(user_id)

        assert len(workflows) == 2
        assert workflow in workflows
        assert workflow2 in workflows

    def test_get_all_workflows_without_user_id(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        workflow_repository.save(user_id, workflow)

        workflows = workflow_repository.get_all()
        assert len(workflows) == 1
        assert workflow in workflows 