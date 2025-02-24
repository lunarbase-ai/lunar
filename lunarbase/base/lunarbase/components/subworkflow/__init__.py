# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Dict

from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.lunar_component import LunarComponent

from lunarbase.modeling.data_models import (
    ComponentInput,
    ComponentModel,
    WorkflowModel,
)
from lunarcore.component.data_types import DataType


class Subworkflow(
    LunarComponent,
    component_name="Subworkflow",
    component_description="""Component for selecting another workflow
    Output (Any): the output of the selected workflow.""",
    input_types={"workflow": DataType.WORKFLOW},
    output_type=DataType.ANY,
    component_group=ComponentGroup.LUNAR,
):
    def __init__(self, **kwargs):
        super().__init__(configuration=kwargs)

    @staticmethod
    def subworkflow_validation(component_model: ComponentModel):
        input_workflow = [
            inp for inp in component_model.inputs if inp.key.lower() == "workflow"
        ][0].value
        workflow = WorkflowModel.parse_obj(input_workflow)
        if not workflow.components:
            raise ValueError("Empty workflow!")
        if len(workflow.dependencies) > 0:
            sources = {dep.source_label for dep in workflow.dependencies}
            targets = {dep.target_label for dep in workflow.dependencies}
            outputs = {tar for tar in targets if tar not in sources}
            if len(outputs) != 1 and (len(outputs) > 1):
                raise ValueError(
                    f"Subworkflow {workflow.name} has more than one output!"
                )
        else:
            if len(workflow.components) > 1:
                ValueError(f"Subworkflow {workflow.name} has more than one output!")

        new_inputs: Dict[str, ComponentInput] = {
            inp.component_id: inp for inp in component_model.inputs[1:]
        }
        for i, component in enumerate(workflow.components):
            input_match = new_inputs.get(component.id)
            if input_match:
                for j, component_input in enumerate(component.inputs):
                    if component_input.key == input_match.key:
                        workflow.components[i].inputs[j].value = input_match.value

        return workflow

    def run(self,  **kwargs: Any):
        raise NotImplementedError("This method is not supposed to run!")
