#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid
import pytest
from lunarbase.modeling.data_models import (
    WorkflowModel,
    ComponentModel,
    ComponentInput,
    ComponentOutput,
)
from lunarcore.component.data_types import DataType

class TestGetWorkflowComponentInputs:
    @pytest.mark.asyncio
    async def test_gets_workflow_component_inputs_when_value_is_none(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        wid = str(uuid.uuid4())
        input_id = str(uuid.uuid4())
        input_value = None
        input_key = "input"
        output_value = None

        components = [
            ComponentModel(
                workflow_id=wid,
                name="Text Input",
                label="TEXTINPUT-01",
                class_name="TextInput",
                description="TextInput",
                group="IO",
                inputs=ComponentInput(
                    key=input_key,
                    data_type=DataType.TEMPLATE,
                    value=input_value,
                    id=input_id,
                    template_variables={}
                ),
                output=ComponentOutput(data_type="TEXT", value=output_value),
            )
        ]
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=wid,
            components=components,
            dependencies=[]
        )

        controller.save(workflow, user_id)

        result = await controller.get_workflow_component_inputs(wid, user_id)

        assert result['inputs'][0]['type'] == DataType.TEMPLATE
        assert result['inputs'][0]['id'] == input_id
        assert result['inputs'][0]['key'] == input_key
        assert result['inputs'][0]['is_template_variable'] is False
        assert result['inputs'][0]['value'] is None

    @pytest.mark.asyncio
    async def test_gets_workflow_component_inputs_when_template_variable_is_none(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        wid = str(uuid.uuid4())
        input_id = str(uuid.uuid4())
        input_value = "Hello, {name}!"
        input_key = "input"
        template_variable_key = "input.name"
        template_variable_value = None
        output_value = None

        components = [
            ComponentModel(
                workflow_id=wid,
                name="Text Input",
                label="TEXTINPUT-01",
                class_name="TextInput",
                description="TextInput",
                group="IO",
                inputs=ComponentInput(
                    key=input_key,
                    data_type=DataType.TEMPLATE,
                    value=input_value,
                    id=input_id,
                    template_variables={template_variable_key: template_variable_value}
                ),
                output=ComponentOutput(data_type="TEXT", value=output_value),
            ),
        ]
        workflow = WorkflowModel(
            name="Test Workflow",
            description="A test workflow",
            id=wid,
            components=components,
            dependencies=[]
        )

        controller.save(workflow, user_id)

        result = await controller.get_workflow_component_inputs(wid, user_id)

        assert result['name'] == workflow.name
        assert result['description'] == workflow.description

        assert result['inputs'][0]['type'] == DataType.TEMPLATE
        assert result['inputs'][0]['id'] == input_id
        assert result['inputs'][0]['key'] == template_variable_key
        assert result['inputs'][0]['is_template_variable'] is True
        assert result['inputs'][0]['value'] == template_variable_value 