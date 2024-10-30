# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect
import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
from typing import Any, Dict, Optional

from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.data_types import DataType
from lunarcore.config import ENVIRONMENT_PREFIX
from lunarcore.errors import ComponentError
from lunarcore.modeling.data_models import (UNDEFINED, ComponentInput,
                                            ComponentModel, ComponentOutput)
from lunarcore.utils import setup_logger

logger = setup_logger("LunarCore")


### GLOBAL VARS TO USE WITH COMPONENTS ###

COMPONENT_DESCRIPTION_TEMPLATE = """
<describe the component in a single sentence>
Output (<type of the output (e.g., List[str])>): <describe the component output in detail>
""".strip()
BASE_CONFIGURATION = {"force_run": False}


class BaseComponent(ABC):
    component_name: str = None
    component_description: str = COMPONENT_DESCRIPTION_TEMPLATE
    input_types: Dict[str, DataType] = None
    output_type: DataType = None
    component_group: ComponentGroup = ComponentGroup.LUNAR
    default_configuration: Dict = None

    def __init_subclass__(
        cls,
        component_name: str,
        input_types: Dict[str, DataType],
        output_type: DataType,
        component_group: ComponentGroup = ComponentGroup.LUNAR,
        component_description: str = COMPONENT_DESCRIPTION_TEMPLATE,
        **kwargs,
    ):
        cls.component_name = component_name
        cls.component_description = component_description
        cls.input_types = input_types
        cls.output_type = output_type
        cls.component_group = component_group
        cls.default_configuration = cls.get_from_env({**kwargs})
        super().__init_subclass__()

    def __init__(
        self,
        model: Optional[ComponentModel] = None,
        configuration: Optional[Dict] = None,
    ):
        config = dict()
        config.update(self.__class__.default_configuration)
        config.update(configuration or dict())

        if model is None:
            self.component_model = self.__class__.to_component_model()
            self.component_model.configuration.update(config)

        else:
            assert model.class_name == self.__class__.__name__, ComponentError(
                f"Invalid class name for component {model.label}. Expected {self.__class__.__name__}, got {model.class_name}!"
            )

            expected_inputs = set(self.__class__.input_types.keys())
            model_inputs = {inp.key for inp in model.inputs}
            assert expected_inputs.issubset(model_inputs), ValueError(
                f"Component {model.label} received invalid inputs. Expected {list(expected_inputs)} got {list(model_inputs)}!"
            )

            config.update(model.configuration)
            this_file = inspect.getfile(self.__class__)
            self.component_model = ComponentModel(
                name=model.name,
                workflow_id=model.workflow_id,
                class_name=self.__class__.__name__,
                label=model.label,
                description=model.description,
                group=self.__class__.component_group,
                inputs=[inp for inp in model.inputs],
                output=model.output,
                configuration=config,
                version=model.version,
                is_custom=model.is_custom,
                is_terminal=model.is_terminal,
                position=model.position,
                timeout=model.timeout,
                component_code=r"{}".format(
                    model.component_code
                    or os.path.join(
                        os.path.basename(os.path.dirname(this_file)),
                        os.path.basename(this_file),
                    )
                ),
            )

        # Treat some configuration, such as force_run, separately.
        # Popped configs need to be put back for frontend consistency.
        # Surely there's a better way. TODO: rethink this.
        self.force_run = (
            self.component_model.configuration.pop("force_run", None)
            or BASE_CONFIGURATION["force_run"]
        )

        # TODO: Is this safe enough?
        self.component_model.configuration = BaseComponent.get_from_env(
            self.component_model.configuration
        )

    @staticmethod
    def get_from_env(data: Dict):
        env_data = dict()
        for key, value in data.items():
            if str(value).startswith(ENVIRONMENT_PREFIX):
                _, _, env_variable = str(value).partition(ENVIRONMENT_PREFIX)
                env_variable_value = os.environ.get(env_variable.strip(), None)
                assert env_variable_value is not None, ComponentError(
                    f"Expected environment variable {env_variable}! Please set it in the environment."
                )
                env_data[key] = env_variable_value
        data.update(env_data)
        return data

    @property
    def configuration(self):
        return self.component_model.configuration

    @property
    def disable_cache(self):
        fr = self.__dict__.get("force_run", "false")
        if isinstance(fr, bool):
            return fr
        return bool(strtobool(fr))

    @classmethod
    def to_component_model(cls):
        this_file = os.path.abspath(inspect.getfile(cls))
        component_model = ComponentModel(
            name=cls.component_name,
            label=None,
            class_name=cls.__name__,
            description=cls.component_description,
            group=cls.component_group,
            inputs=[],
            output=ComponentOutput(data_type=cls.output_type),
            configuration=cls.default_configuration,
            component_code=os.path.relpath(this_file),
        )
        inputs = [
            ComponentInput(
                key=_in_name, data_type=_in_type, component_id=component_model.id
            )
            for _in_name, _in_type in cls.input_types.items()
        ]
        component_model.inputs = inputs
        return component_model

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
        inputs = BaseComponent.get_from_env(inputs)

        # Type compatibility check & mapping (for loops)
        mappings, non_mappings = dict(), inputs.copy()

        for in_name, in_value in inputs.items():
            try:
                if (
                    self.__class__.input_types[in_name] != DataType.LIST
                    and isinstance(in_value, list)
                    and len(in_value) > 0
                    and self.__class__.input_types[in_name].type() == type(in_value[0])
                ):
                    mappings[in_name] = in_value
                    non_mappings.pop(in_name)
            except KeyError as e:
                raise ComponentError(f"Unexpected input. Full error message: {str(e)}!")

        if len(mappings) == 0:
            run_result = self.run(**inputs)
        else:
            run_result = []

            mapped_keys = list(mappings.keys())
            for mapped_ins in zip(*mappings.values()):
                interation_inputs = dict(zip(mapped_keys, mapped_ins))
                interation_inputs.update(non_mappings)
                iteration_result = self.run(**interation_inputs)
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

    @abstractmethod
    def run(
        self,
        **inputs: Any,
    ):
        pass
