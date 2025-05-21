#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestTmpSaveWorkflow:
    def test_tmp_saves_workflow_returns_saved_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        saved_workflow = workflow_repository.tmp_save(user_id, workflow)

        assert saved_workflow.id == workflow.id
        
    def test_tmp_saves_workflow_in_correct_path(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        workflow_repository.tmp_save(user_id, workflow)

        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")

        assert path.exists() 