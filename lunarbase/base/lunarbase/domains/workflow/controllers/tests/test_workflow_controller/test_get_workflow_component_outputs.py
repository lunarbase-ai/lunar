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

class TestGetWorkflowComponentOutputs:
    @pytest.mark.asyncio
    async def test_gets_workflow_component_outputs(self, controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        wid = str(uuid.uuid4())
        input_id = str(uuid.uuid4())
        input_value = "Hello, {name}!"
        input_key = "input"
        template_variable_key = "input.name"
        template_variable_value = "John"
        output_value = "Hello, John!"
        component_label = "TEXTINPUT-01"

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

        result = await controller.get_workflow_component_outputs(wid, user_id)

        assert result == [component_label] 