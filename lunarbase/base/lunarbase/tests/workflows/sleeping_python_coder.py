from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    WorkflowModel,
    ComponentDependency,
)
from lunarbase.tests.fixtures import workflow_controller


@pytest.mark.asyncio
async def test_sleeping_python_coder(workflow_controller):
    wid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=wid,
            name="TextInput",
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
        ),
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

    try:
        result = await workflow_controller.run(workflow)
    finally:
        await workflow_controller.delete(
            workflow.id, workflow_controller.config.DEFAULT_USER_PROFILE
        )
    result_value = result.get(components[-1].label, dict()).get("output", dict()).get("value")
    assert result_value is not None and result_value == "abcdr"
