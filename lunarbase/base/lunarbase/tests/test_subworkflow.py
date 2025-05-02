from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    WorkflowModel,
    ComponentDependency,
)

@pytest.fixture
def subworkflow():
    swid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=swid,
            name="TextInput",
            class_name="TextInput",
            label="TEXTINPUT-01",
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
            workflow_id=swid,
            name="PythonCoder",
            class_name="PythonCoder",
            label="PYTHONCODER-02",
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
    
    subworkflow = WorkflowModel(
        id=swid,
        name="Sorted set subworkflow",
        description="Sorted set subworkflow",
        components=components,
        dependencies=[
            ComponentDependency(
                component_input_key="code",
                source_label=components[0].label,
                target_label=components[1].label,
                template_variable_key="code.value",
            ),
        ],
    )
    return subworkflow


@pytest.mark.asyncio
async def test_subworkflow(workflow_controller, subworkflow):
    wid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=wid,
            name="Subworkflow",
            class_name="Subworkflow",
            label="SUBWORKFLOW-01",
            description="Subworkflow",
            group="LUNAR",
            inputs=ComponentInput(
                key="workflow",
                data_type="WORKFLOW",
                value=subworkflow.dict(),
            ),
            output=ComponentOutput(data_type="ANY", value=None),
        ),
        ComponentModel(
            workflow_id=wid,
            name="Text Input",
            label="TEXTINPUT-02",
            class_name="TextInput",
            description="TextInput",
            group="IO",
            inputs=ComponentInput(
                key="input",
                data_type="TEMPLATE",
                value="{sub_result}",
                template_variables={"input.sub_result": None},
            ),
            output=ComponentOutput(data_type="TEXT", value=None),
        )
    ]

    workflow = WorkflowModel(
        id=wid,
        name="Parent workflow",
        description="Parent test workflow with subworkflow",
        components=components,
        dependencies=[
            ComponentDependency(
                component_input_key="input",
                source_label=components[0].label,
                target_label=components[1].label,
                template_variable_key="input.sub_result",
            ),
        ],
    )

    result = await workflow_controller.run(workflow, user_id=workflow_controller.config.DEFAULT_USER_TEST_PROFILE)
    result_value = result[components[-1].label].output.value
    assert result_value == "abcdr"
