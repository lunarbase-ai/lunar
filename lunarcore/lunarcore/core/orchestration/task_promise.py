# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import types
from typing import Any

from lunarcore.core.component import BaseComponent
from lunarcore.errors import ComponentError


class TaskPromise:
    def __init__(self, component: BaseComponent):
        self.component = component

    def run(self, **inputs: Any):
        model_inputs = {inp.key: inp for inp in self.component.component_model.inputs}
        for in_name, in_value in inputs.items():
            try:
                model_inputs[in_name].value = in_value
            except KeyError:
                raise ComponentError(
                    f"No such input named {in_name} for component {self.component.component_model.label}!"
                )

        run_inputs = {key: value.value for key, value in model_inputs.items()}
        self.component.set_inputs(**run_inputs)

        run_output = self.component.run(**run_inputs)

        if not isinstance(run_output, types.GeneratorType):
            self.component.set_output(run_output)
            yield self.component.component_model
        else:
            for result in run_output:
                self.component.set_output(result)
                yield self.component.component_model
