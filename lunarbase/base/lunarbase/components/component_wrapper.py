# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib
import os
from distutils.util import strtobool
from typing import Any, Dict, Optional

from lunarbase.components.errors import ComponentError
from lunarbase.config import ENVIRONMENT_PREFIX
from lunarbase.modeling.data_models import (
    UNDEFINED,
    ComponentInput,
    ComponentModel,
    ComponentOutput,
)
from lunarbase.utils import setup_logger
from lunarcore.component.data_types import DataType
from lunarcore.component.lunar_component import LunarComponent

from lunarbase import LUNAR_CONTEXT

logger = setup_logger("Lunarbase")

BASE_CONFIGURATION = {"force_run": False}


class ComponentWrapper:
    def __init__(self, component: ComponentModel):
        # self.component_model = component

        try:
            registered_component = LUNAR_CONTEXT.lunar_registry.get_by_class_name(
                component.class_name
            )
            if registered_component is None:
                raise ComponentError(
                    f"Error encountered while trying to load {component.class_name}! "
                    f"Component not found in {LUNAR_CONTEXT.lunar_registry.get_component_names()}. "
                )

            component_model = registered_component.component_model

            self.force_run = (
                    component_model.configuration.pop("force_run", None)
                    or BASE_CONFIGURATION["force_run"]
            )

            component_model.configuration = ComponentWrapper.update_configuration(
                component.configuration
            )

            component_module = importlib.import_module(registered_component.module_name)
            instance_class = getattr(component_module, component_model.class_name)
            self.component_instance = instance_class(
                configuration=component_model.configuration
            )

            # This will need to be rethought
            self.component_model = component_model
            self.component_model.inputs = component.inputs
            self.component_model.output = component.output

        except Exception as e:
            raise ComponentError(
                f"Failed to instantiate component {self.component_model.label}: {str(e)}!"
            )

        # self.component_model.configuration.update(
        #     ComponentWrapper.update_configuration(self.component_instance.configuration)
        # )

        # Treat some configuration, such as force_run, separately.
        # Popped configs need to be put back for frontend consistency.
        # Surely there's a better way. TODO: rethink this.

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
    def get_from_env(data: Dict):
        env_data = dict()
        for key, value in data.items():
            if str(value).startswith(ENVIRONMENT_PREFIX):
                _, _, env_variable = str(value).partition(ENVIRONMENT_PREFIX)
                env_variable_value = os.environ.get(env_variable.strip(), None)
                assert env_variable_value is not None, ValueError(
                    f"Expected environment variable {env_variable}! Please set it in the environment."
                )
                env_data[key] = env_variable_value
        data.update(env_data)
        return data

    @staticmethod
    def update_configuration(current_configuration):
        # Configuration updated from env and expanded from datasources/llms at instantiation time
        current_configuration = ComponentWrapper.get_from_env(current_configuration)

        if current_configuration.get("datasource") is not None:
            ds = LUNAR_CONTEXT.lunar_registry.get_data_source(
                current_configuration["datasource"]
            )
            if ds is not None:
                connection_details = ds.connection_attributes.dict()
                current_configuration.update(connection_details)
        current_configuration.pop("datasource", None)

        if current_configuration.get("llm") is not None:
            llm = LUNAR_CONTEXT.lunar_registry.get_llm(current_configuration["llm"])
            if llm is not None:
                connection_details = llm.connection_attributes.dict()
                current_configuration.update(connection_details)
        current_configuration.pop("llm", None)

        return current_configuration

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

    def run(self, **run_kwargs):
        return self.component_instance.run(**run_kwargs)

    def run_in_workflow(self):
        """
        Input are expected to come from Component model
        """
        user_context = LUNAR_CONTEXT.lunar_registry.get_user_context()
        inputs = []
        for inp in self.component_model.inputs:
            if inp.data_type in [DataType.FILE] and isinstance(inp.value, str):
                ds = LUNAR_CONTEXT.lunar_registry.get_data_source(inp.value)
                if ds is not None and user_context is not None:
                    inp.value = ds.to_component_input(user_context.get("file_root"))

            inputs.append(inp)

        inputs = {inp.key: inp.resolve_template_variables() for inp in inputs}

        inputs = {
            key: value if value != UNDEFINED else None for key, value in inputs.items()
        }

        # Replace environment
        inputs = ComponentWrapper.get_from_env(inputs)

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
