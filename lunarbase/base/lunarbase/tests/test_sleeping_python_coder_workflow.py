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
def sleeping_python_coder_workflow():
    wid = "fd623681-b227-4cb2-bacf-c12a831b5b0a"
    components = [
        ComponentModel(
            workflow_id=wid,
            name="Text Input",
            label="TEXTINPUT-01",
            class_name="TextInput",
            description="TextInput",
            group="IO",
            inputs=ComponentInput(
                key="input",
                data_type="TEMPLATE",
                value="abracadabra",
            ),
            output=ComponentOutput(data_type="TEXT", value=None),
        ),
        ComponentModel(
            workflow_id=wid,
            name="Sleep",
            label='SLEEP-02',
            class_name="Sleep",
            description="Sleep",
            group="Utils",
            inputs=[
                ComponentInput(
                    key="input",
                    data_type="ANY",
                    value=None,
                ),
                ComponentInput(key="timeout", data_type="INT", value=1),
            ],
            output=ComponentOutput(data_type="TEXT", value=None),
        ),
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
                value="""from sortedcontainers import SortedSet
ss = SortedSet("{value}")
ss = "".join(ss)
result = ss""",
                template_variables={"code.value": None},
            ),
            output=ComponentOutput(data_type="ANY", value=None),
        )
    ]

    workflow = WorkflowModel(
        id=wid,
        name="The Sleeping Python coder",
        description="The Sleeping Python coder",
        components=components,
        dependencies=[
            ComponentDependency(
                component_input_key="input",
                source_label=components[0].label,
                target_label=components[1].label,
                template_variable_key=None,
            ),
            ComponentDependency(
                component_input_key="code",
                source_label=components[1].label,
                target_label=components[2].label,
                template_variable_key="code.value",
            ),
        ],
    )
    return workflow, components

@pytest.mark.asyncio
async def test_existing_sleeping_python_coder_workflow(workflow_controller, sleeping_python_coder_workflow):
    workflow, components = sleeping_python_coder_workflow

    workflow_controller.save(workflow, workflow_controller.config.DEFAULT_USER_TEST_PROFILE)

    result = await workflow_controller.run(workflow, user_id=workflow_controller.config.DEFAULT_USER_TEST_PROFILE)
    result_value = result[components[-1].label].output.value
    assert result_value == "abcdr"

@pytest.mark.asyncio
async def test_new_sleeping_python_coder_workflow(workflow_controller, sleeping_python_coder_workflow):
    workflow, components = sleeping_python_coder_workflow

    workflow_controller.save(workflow, workflow_controller.config.DEFAULT_USER_TEST_PROFILE)

    result = await workflow_controller.run(workflow, user_id=workflow_controller.config.DEFAULT_USER_TEST_PROFILE)
    result_value = result[components[-1].label].output.value
    assert result_value == "abcdr"
