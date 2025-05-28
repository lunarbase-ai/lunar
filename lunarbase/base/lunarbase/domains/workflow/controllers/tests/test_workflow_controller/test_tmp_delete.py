#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import pytest

class TestTmpDelete:
    def test_deletes_temporary_saved_workflow(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=str(uuid.uuid4()),
        )
        path = Path(config.USER_DATA_PATH, user_id, config.TMP_PATH, f"{workflow.id}.json")
        controller.tmp_save(workflow, user_id)

        assert path.exists()

        assert controller.tmp_delete(workflow.id, user_id)

        assert not path.exists() 