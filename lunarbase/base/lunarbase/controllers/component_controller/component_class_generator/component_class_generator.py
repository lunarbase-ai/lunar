# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from lunarcore.core.data_models import ComponentModel


def get_component_code(component: ComponentModel) -> str:

    # Generate the input types as a dictionary string
    inputs = '{' + ', '.join(
        [f'"{input.key}": DataType.{input.data_type}' for input in component.inputs]) + '}'

    # Extract configuration settings
    configuration = component.configuration
    settings = ''.join([f'{conf}="{configuration[conf]}",\n  ' for conf in configuration])

    requirements = "\n".join(
        [f"from {requirement} import ..." for requirement in component.component_code_requirements])

    run_method = f"def run(self, {', '.join([component_input.key for component_input in component.inputs])}):\n"
    if component.component_code:
        run_method = component.component_code

    component_group = "None"
    if component.group:
        component_group = f"ComponentGroup.{component.group.name}"

    # Define the component class with its attributes and methods
    component_class_definition = f"""from typing import Any, Optional

from lunarcore.core.component import BaseComponent
from lunarcore.core.typings.components import ComponentGroup
from lunarcore.core.data_models import ComponentInput, ComponentModel
from lunarcore.core.typings.datatypes import DataType

{requirements}

class {component.name.replace(" ", "")}(
  BaseComponent,
  component_name="{component.name}",
  component_description=\"\"\"{component.description}\"\"\",
  input_types={inputs},
  output_type=DataType.{component.output.data_type},
  component_group={component_group},
  {settings}
):
  def __init__(self, model: Optional[ComponentModel] = None, **kwargs: Any):
    super().__init__(model=model, configuration=kwargs)

  {run_method}
"""
    return component_class_definition
