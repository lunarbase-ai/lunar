#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestTmpDeleteWorkflow:
    def test_tmp_deletes_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        workflow_repository.tmp_save(user_id, workflow)

        assert path.exists()

        workflow_repository.tmp_delete(user_id, workflow.id)
        assert not path.exists() 