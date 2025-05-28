#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path
from lunarbase.modeling.data_models import WorkflowModel
import uuid


class TestSaveWorkflow:
    def test_saves_workflow_returns_saved_workflow(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )

        saved_workflow = workflow_repository.save(user_id, workflow)

        assert saved_workflow.id == workflow.id

    def test_saves_workflow_in_correct_path(self, workflow_repository, config, path_resolver):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        workflow = WorkflowModel(
            name="Workflow Name",
            description="Workflow Description",
            id=str(uuid.uuid4()),
        )
    
        workflow_repository.save(user_id, workflow)

        path = path_resolver.get_user_workflow_path(workflow.id, user_id)
        
        assert Path(path).exists()

    def test_saves_default_workflow_if_none_provided(self, workflow_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        saved_workflow = workflow_repository.save(user_id)

        assert saved_workflow.name == "Untitled"
        assert saved_workflow.description == "" 