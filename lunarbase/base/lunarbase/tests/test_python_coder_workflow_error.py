#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    WorkflowModel,
    ComponentDependency,
)
import logging

logging.basicConfig(level=logging.INFO)

@pytest.fixture
def python_coder_workflow_error():
    wid = "fd623681-b227-4cb2-bacf-c12a831b5b0a"
    components = [
        ComponentModel(
            workflow_id=wid,
            name="PythonCoder",
            label='PYTHONCODER-03',
            class_name="PythonCoder",
            description="PythonCoder",
            group="CODERS",
            inputs=ComponentInput(
                key="code",
                data_type="Code",
                value="""result = 5/0""",
                template_variables={},
            ),
            output=ComponentOutput(data_type="ANY", value=None),
        )
    ]

    workflow = WorkflowModel(
        id=wid,
        name="The Sleeping Python coder",
        description="The Sleeping Python coder",
        components=components,
        dependencies=[],
    )
    return workflow, components

@pytest.mark.asyncio
async def test_existing_python_coder_workflow_error(workflow_controller, python_coder_workflow_error):
    workflow, components = python_coder_workflow_error

    workflow_controller.save(workflow, workflow_controller.config.DEFAULT_USER_TEST_PROFILE)

    result = await workflow_controller.run(workflow, user_id=workflow_controller.config.DEFAULT_USER_TEST_PROFILE)
    result_value = result[components[-1].label]
    assert result_value == "division by zero"
