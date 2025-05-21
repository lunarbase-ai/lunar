#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestDeleteWorkflow:
    def test_deletes_workflow(self, workflow_repository, config, path_resolver):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description", 
            id=str(uuid.uuid4()),
        )
        workflow_repository.save(user_id, workflow)

        path = path_resolver.get_user_workflow_path(workflow.id, user_id)

        assert Path(path).exists()

        workflow_repository.delete(user_id, workflow.id)

        assert not Path(path).exists() 