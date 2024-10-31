# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio
import json
import os
import shutil
from collections import namedtuple
from enum import Enum
from typing import Dict, List, Union
from uuid import uuid4

import pytest
from lunarbase.controllers.workflow_controller import WorkflowController
from lunarbase.modeling.data_models import ComponentInput, WorkflowModel
from pydantic import BaseModel, Field, field_validator

from lunarbase import COMPONENT_REGISTRY

RUNTIME_USER: str = "admin"

TEST_DATA = []


class AssertionOperator(Enum):
    EQUALS = "EQUALS"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"

    def apply(self, left_operand: str, right_operand: str):
        left_operand = left_operand.strip().strip('"').lower()
        right_operand = right_operand.strip().strip('"').lower()
        if self == AssertionOperator.EQUALS:
            assert (
                left_operand == right_operand
            ), f"<{left_operand}> not equal to <{right_operand}>"
        elif self == AssertionOperator.CONTAINS:
            assert (
                right_operand in left_operand
            ), f"<{left_operand}> not in <{right_operand}>"
        elif self == AssertionOperator.STARTS_WITH:
            assert left_operand.startswith(
                right_operand
            ), f"<{left_operand}> does not start with <{right_operand}>"
        elif self == AssertionOperator.ENDS_WITH:
            assert left_operand.endswith(
                right_operand
            ), f"<{left_operand}> does not end with <{right_operand}>"
        else:
            raise ValueError(f"Unknown assertion operator {self.value}")


ComponentAssertion = namedtuple("ComponentAssertion", "operator value")


class ComponentTestModel(BaseModel):
    name: str = Field(default=...)
    inputs: List[ComponentInput] = Field(default_factory=list)
    configuration: Dict = Field(default_factory=dict)
    assertions: Dict[str, Union[Dict, List[ComponentAssertion]]] = Field(
        default_factory=dict
    )

    @field_validator("assertions")
    @classmethod
    def validate_assertions(cls, value):
        valid_assertions = dict()
        for ref, assertion in value.items():
            validated = []
            if isinstance(assertion, dict):
                validated.extend(
                    [
                        ComponentAssertion(AssertionOperator(str(op).upper()), val)
                        for op, val in assertion.items()
                    ]
                )
            else:
                validated.append(assertion)
            valid_assertions[ref] = validated
        return valid_assertions


class ComponentTestDataLoader:
    @staticmethod
    def get_test_data(test_root: str):
        for test_dir in os.listdir(test_root):
            if not os.path.isdir(test_dir):
                continue

            test_dir = os.path.join(test_root, test_dir)
            all_tests = [
                os.path.join(test_dir, json_file)
                for json_file in os.listdir(test_dir)
                if json_file.endswith(".json")
            ]
            for test_file_path in all_tests:
                with open(test_file_path, "r") as test_file:
                    # print(json.load(test_file))
                    test_data = ComponentTestModel.model_validate(json.load(test_file))
                    yield test_data


test_cases = list(
    ComponentTestDataLoader.get_test_data(os.path.join(os.path.dirname(__file__)))
)


@pytest.mark.parametrize("test_definition", test_cases)
def test_component(test_definition):
    """
    ToDo: Environment specific configuration, e.g., API keys.
    Parameters
    ----------
    test_definition

    Returns
    -------

    """

    if len(COMPONENT_REGISTRY.components) == 0:
        asyncio.run(COMPONENT_REGISTRY.load_components())

    controller = WorkflowController(COMPONENT_REGISTRY.config)
    _, component = COMPONENT_REGISTRY.get_by_class_name(test_definition.name)
    component.configuration.update(**test_definition.configuration)
    component.inputs = test_definition.inputs

    workflow = WorkflowModel(
        id=str(uuid4()),
        user_id=RUNTIME_USER,
        name=f"Test {test_definition.name}",
        description=f"Test workflow for component {test_definition.name}",
        components=[component],
    )

    out = asyncio.run(controller.run(workflow, user_id=RUNTIME_USER))
    venv_dir = os.path.join(
        controller.config.LUNAR_STORAGE_BASE_PATH,
        RUNTIME_USER,
        controller.config.USER_WORKFLOW_ROOT,
        controller.config.USER_WORKFLOW_VENV_ROOT,
        workflow.id,
    )

    shutil.rmtree(venv_dir)

    output_component_model = list(out.values())[-1]
    if isinstance(output_component_model, str):
        raise AssertionError(
            f"A string output likely means an error: {output_component_model}!"
        )
    output = output_component_model.get("output", dict())

    assert not isinstance(
        output_component_model, str
    ), f"Failed to run test for component: {output_component_model}"
    for operand, assertions in test_definition.assertions.items():
        if operand == "*":
            operand = output.get("value", "").strip()
        else:
            operand = output.get("value", dict()).get(operand, "").strip()
        for ass in assertions:
            ass.operator.apply(
                operand,
                ass.value,
            )


if __name__ == "__main__":
    test_component(test_cases[1])
