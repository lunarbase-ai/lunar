from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    WorkflowModel,
    ComponentDependency,
)


@pytest.mark.asyncio
async def test_writer_subworkflow(workflow_controller, empty_local_file_datasource):
    swid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=swid,
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
            workflow_id=swid,
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

    wid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=wid,
            name="Subworkflow",
            class_name="Subworkflow",
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
            name="Text File Writer",
            class_name="TextFileWriter",
            description="Text File Writer",
            group="IO",
            inputs=[
                ComponentInput(
                    key="input_file",
                    data_type="File",
                    value=empty_local_file_datasource.id,
                ),
                ComponentInput(key="input_text", data_type="TEXT", value=None),
            ],
            output=ComponentOutput(data_type="NULL", value=None),
        ),
    ]
    workflow = WorkflowModel(
        id=wid,
        name="Parent workflow",
        description="Parent test workflow with one subworkflow",
        components=components,
        dependencies=[
            ComponentDependency(
                component_input_key="input_text",
                source_label=components[0].label,
                target_label=components[1].label,
                template_variable_key=None,
            ),
        ],
    )

    try:
        await workflow_controller.run(workflow)
    finally:
        workflow_controller.delete(
            workflow.id, workflow_controller.config.DEFAULT_USER_PROFILE
        )

    _file = empty_local_file_datasource.to_component_input(
        workflow_controller.persistence_layer.get_user_file_root(
            workflow_controller.config.DEFAULT_USER_PROFILE
        )
    )
    with open(_file.path, "r") as f:
        assert f.read() == "abcdr"
