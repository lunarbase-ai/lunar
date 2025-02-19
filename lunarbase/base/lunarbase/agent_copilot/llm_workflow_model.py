# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from typing import List, Optional

from pydantic import BaseModel, Field


class LLMTemplateVariable(BaseModel):
    template_variable_name: str = Field(...)
    template_variable_value: str = Field(...)


class LLMComponentInput(BaseModel):
    input_name: str = Field(...)
    input_value: str = Field(..., description="The component input value might contain input values. e.g.: Hello, {{name}}")
    template_variables: List[LLMTemplateVariable] = Field(description="A list of the input value template variables")


class LLMComponentModel(BaseModel):
    name: str = Field(description="The name of the component.")
    identifier: str = Field(description="It's the component reference")
    inputs: List[LLMComponentInput] = Field(description="A list of input name to value. It must contain all the inputs of the available component. Values should be filled depending on user intent")


class LLMUndefinedComponentModel(BaseModel):
    name: str = Field(description="The name of the component.")
    identifier: str = Field(description="The identifier of the component. It's a random string of 8 characters")
    description: str = Field(description="The description of the component. It's a textual representation of the component")
    inputs: List[LLMComponentInput] = Field(..., description="A list of input name to value")


class LLMDependencyModel(BaseModel):
    source: str = Field(description="The source component identifier. It's a reference to the component that will execute first")
    target: str = Field(description="The target component identifier. It's a reference to the component that depends on the source component to execute")
    target_input: str = Field(description="The input name of the target component")
    target_template_variable_name: Optional[str] = Field(description="The template variable name, if the target is a template variable.")


class LLMWorkflowModel(BaseModel):
    name: str = Field(description="The name of the workflow")
    description: str = Field(description="The description of the workflow")
    components: List[LLMComponentModel] = Field(
        description="A list with all workflow components.",
    )
    undefined_components: List[LLMUndefinedComponentModel] = Field(
        description="A list of random component identifier to textual component description",
        default_factory=list
    )
    dependencies: List[LLMDependencyModel] = Field(
        description="A list of dependencies denoting graph edges",
        default_factory=list
    )


class LLMDependencies(BaseModel):
    dependencies: List[LLMDependencyModel] = Field(
        description="A list of dependencies denoting graph edges",
        default_factory=list
    )
