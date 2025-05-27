#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from lunarcore.component.data_types import DataType
from typing import Optional
from lunarbase.modeling.data_models import ComponentModel


def update_inputs(
    current_task: ComponentModel,
    upstream_task: ComponentModel,
    upstream_label: str,
    input_key: str,
    template_key: Optional[str] = None,
):
    for i in range(len(current_task.inputs)):
        if current_task.inputs[i].key != input_key:
            continue

        if template_key is not None:
            template_key_factors = template_key.split(".", maxsplit=1)
            if len(template_key_factors) < 2:
                template_key = f"{input_key}.{template_key}"
            elif template_key_factors[0] != input_key:
                raise ValueError(
                    f"Something is wrong with the template variables. Expected parent variable {input_key}, got {template_key_factors[0]}!"
                )

            current_task.inputs[i].template_variables[
                template_key
            ] = upstream_task.output.value
        elif current_task.inputs[i].data_type == DataType.AGGREGATED:
            if not isinstance(current_task.inputs[i].value, dict):
                current_task.inputs[i].value = {}
            current_task.inputs[i].value[upstream_label] = upstream_task.output.value
        else:
            current_task.inputs[i].value = upstream_task.output.value

        break
    return current_task