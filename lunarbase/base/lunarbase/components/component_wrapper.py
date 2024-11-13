# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib
import inspect
from distutils.util import strtobool
from typing import Any, Dict, Optional, Union

from lunarbase.components.errors import ComponentError
from lunarbase.modeling.data_models import (
    UNDEFINED,
    ComponentInput,
    ComponentModel,
    ComponentOutput,
)
from lunarbase.utils import setup_logger
from lunarcore.component.data_types import DataType
from lunarcore.component.lunar_component import LunarComponent

from lunarbase import REGISTRY

from pathlib import Path

logger = setup_logger("Lunarbase")

BASE_CONFIGURATION = {"force_run": False}


class ComponentWrapper:
    def __init__(self, component: Union[LunarComponent, ComponentModel]):
        if isinstance(component, LunarComponent):
            self.component_instance = component
            self.component_model = ComponentWrapper.component_model_factory(component)

        else:
            self.component_model = component
            self.component_instance = ComponentWrapper.component_instance_factory(
                component
            )

        self.component_model.configuration.update(self.component_instance.configuration)

        # Treat some configuration, such as force_run, separately.
        # Popped configs need to be put back for frontend consistency.
        # Surely there's a better way. TODO: rethink this.
        self.force_run = (
            self.component_model.configuration.pop("force_run", None)
            or BASE_CONFIGURATION["force_run"]
        )

        self.component_model.configuration = LunarComponent.get_from_env(
            self.component_model.configuration
        )

    @property
    def configuration(self):
        return self.component_model.configuration

    @property
    def disable_cache(self):
        fr = self.__dict__.get("force_run", "false")
        if isinstance(fr, bool):
            return fr
        return bool(strtobool(fr))

    @staticmethod
    def assemble_component_instance_type(component: ComponentModel):
        def constructor(
            self,
            configuration: Optional[Dict] = None,
        ):
            super(self.__class__, self).__init__(configuration=configuration)

        _class = type(
            component.class_name,
            (LunarComponent,),
            {"__init__": constructor, **component.get_callables()},
            component_name=component.name,
            component_description=component.description,
            input_types={inp.key: inp.data_type for inp in component.inputs},
            output_type=component.output.data_type,
            component_group=component.group,
        )
        return _class

    @staticmethod
    def component_instance_factory(component_model: ComponentModel):
        try:
            registered_component = REGISTRY.get_by_class_name(
                component_model.class_name
            )
            if registered_component is None:
                raise ComponentError(
                    f"Error encountered while trying to load {component_model.class_name}! "
                    f"Component not found in {REGISTRY.get_component_names()}. "
                )

            component_model = registered_component.component_model
            component_module = importlib.import_module(registered_component.module_name)

            instance_class = getattr(component_module, component_model.class_name)
            instance = instance_class(configuration=component_model.configuration)

        except Exception as e:
            raise ComponentError(
                f"Failed to instantiate component {component_model.label}: {str(e)}!"
            )
        return instance

    @staticmethod
    def component_model_factory(component_instance: LunarComponent):
        registered_component = REGISTRY.get_by_class_name(
            component_instance.__class__.__name__
        )
        if registered_component is not None:
            return registered_component.component_model

        class_file = inspect.getfile(component_instance.__class__)
        component_model = ComponentModel(
            name=component_instance.__class__.component_name,
            label=None,
            class_name=component_instance.__name__,
            description=component_instance.__class__.component_description,
            group=component_instance.__class__.component_group,
            inputs=[],
            output=ComponentOutput(data_type=component_instance.__class__.output_type),
            configuration=component_instance.configuration,
            component_code=Path(class_file).relative_to(
                REGISTRY.config.COMPONENT_LIBRARY_PATH
            ),
        )
        inputs = [
            ComponentInput(
                key=_in_name, data_type=_in_type, component_id=component_model.id
            )
            for _in_name, _in_type in component_instance.__class__.input_types.items()
        ]
        component_model.inputs = inputs
        return component_model

    def run(self, **run_kwargs):
        return self.component_instance.run(**run_kwargs)

    def run_in_workflow(self):
        """
        Input are expected to come from Component model
        """
        inputs = [
            ComponentInput.model_validate(dict(inp))
            for inp in self.component_model.inputs
        ]

        inputs = {inp.key: inp.resolve_template_variables() for inp in inputs}
        inputs = {
            key: value if value != UNDEFINED else None for key, value in inputs.items()
        }

        # Replace environment
        inputs = LunarComponent.get_from_env(inputs)

        # Type compatibility check & mapping (for loops)
        mappings, non_mappings = dict(), inputs.copy()

        for in_name, in_value in inputs.items():
            try:
                if (
                    self.component_instance.__class__.input_types[in_name]
                    != DataType.LIST
                    and isinstance(in_value, list)
                    and len(in_value) > 0
                    and self.component_instance.__class__.input_types[in_name].type()
                    == type(in_value[0])
                ):
                    mappings[in_name] = in_value
                    non_mappings.pop(in_name)
            except KeyError as e:
                raise ComponentError(f"Unexpected input. Full error message: {str(e)}!")

        if len(mappings) == 0:
            run_result = self.component_instance.run(**inputs)
        else:
            run_result = []

            mapped_keys = list(mappings.keys())
            for mapped_ins in zip(*mappings.values()):
                interation_inputs = dict(zip(mapped_keys, mapped_ins))
                interation_inputs.update(non_mappings)
                iteration_result = self.component_instance.run(**interation_inputs)
                run_result.append(iteration_result)

        self.set_output(run_result)

        # Restoring force_run
        self.component_model.configuration["force_run"] = self.force_run

        return self.component_model

    def set_output(self, result):
        if isinstance(result, ComponentOutput):
            self.component_model.output = ComponentOutput.model_validate(result.dict())
        elif isinstance(result, ComponentInput):
            self.component_model.output = ComponentOutput(
                data_type=result.data_type, value=result.value
            )
        else:
            self.component_model.output.value = result

    def set_inputs(self, **inputs: Any):
        for i, inp in enumerate(self.component_model.inputs):
            value = inputs.get(inp.key, None)
            if value is not None:
                self.component_model.inputs[i].value = value
                _ = inputs.pop(inp.key, None)

        if len(inputs):
            raise ComponentError(
                f"The following inputs have not been found in component {self.component_model.label}: {list(inputs.keys())}"
            )
