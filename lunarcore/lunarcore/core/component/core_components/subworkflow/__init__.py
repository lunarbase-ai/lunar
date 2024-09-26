# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Optional, Dict

from lunarcore.core.component import BaseComponent
from lunarcore.core.typings.components import ComponentGroup
from lunarcore.core.data_models import ComponentInput, ComponentModel, WorkflowModel
from lunarcore.core.typings.datatypes import DataType


class Subworkflow(
    BaseComponent,
    component_name="Subworkflow",
    component_description="""Component for selecting another workflow
    Output (Any): the output of the selected workflow.""",
    input_types={"Workflow": DataType.WORKFLOW},
    output_type=DataType.ANY,
    component_group=ComponentGroup.LUNAR,
):
    def __init__(self, model: Optional[ComponentModel] = None, **kwargs):
        super().__init__(model=model, configuration=kwargs)

    def validate(self):
        input_workflow = [inp for inp in self.component_model.inputs if inp.key == "Workflow"][0].value
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
            inp.component_id: inp for inp in self.component_model.inputs[1:]
        }
        for i, component in enumerate(workflow.components):
            input_match = new_inputs.get(component.id)
            if input_match:
                for j, component_input in enumerate(component.inputs):
                    if component_input.key == input_match.key:
                        workflow.components[i].inputs[j].value = input_match.value

        return workflow

    def run(self, inputs: [ComponentInput], **kwargs: Any):
        raise NotImplemented("This method is not supposed to run!")