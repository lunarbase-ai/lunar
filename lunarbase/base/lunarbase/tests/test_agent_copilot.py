#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from lunarcore.component.data_types import DataType

from lunarbase.agent_copilot import LLMWorkflowMapper
from lunarbase.agent_copilot.llm_workflow_model import LLMComponentModel, LLMDependencyModel, LLMWorkflowModel
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel, ComponentDependency, ComponentInput, \
    ComponentOutput


def test_to_workflow(registry):
    llm_workflow = LLMWorkflowModel(
        name="TestWorkflow",
        description="A test workflow",
        components=[LLMComponentModel(name="PythonCoder", identifier="comp1", inputs=[])],
        dependencies=[]
    )

    mapper = LLMWorkflowMapper(lunar_registry=registry)
    workflow = mapper.to_workflow(llm_workflow)

    assert workflow.name == llm_workflow.name
    assert workflow.description == llm_workflow.description
    assert len(workflow.components) == 1
    assert workflow.components[0].label == "comp1"


def test_to_component(registry):
    mock_component = ComponentModel(
        name="Mock",
        description="",
        class_name="MockComponent",
        inputs=[],
        output=ComponentOutput(data_type=DataType.ANY, value="")
    )

    mapper = LLMWorkflowMapper(lunar_registry=registry)
    mapper._component_library_index = {"MockComponent": mock_component}

    llm_component = LLMComponentModel(name="MockComponent", identifier="comp1", inputs=[])

    component = mapper._to_component(llm_component, "workflow123")

    assert component.label == "comp1"
    assert component.workflow_id == "workflow123"


def test_to_dependency():
    llm_dependency = LLMDependencyModel(
        source="comp1",
        target="comp2",
        target_input="inputX",
        target_template_variable_name=None
    )

    dependency = LLMWorkflowMapper._to_dependency(llm_dependency)

    assert dependency.source_label == "comp1"
    assert dependency.target_label == "comp2"
    assert dependency.component_input_key == "inputX"


def test_to_llm_workflow():
    component = ComponentModel(
        name="Python coder",
        description="description",
        class_name="PythonCoder",
        label="comp1",
        inputs=[ComponentInput(key="code", data_type=DataType.CODE, value="", template_variables={})],
        output=ComponentOutput(data_type=DataType.ANY, value="")
    )
    workflow = WorkflowModel(
        name="TestWorkflow",
        description="A test workflow",
        components=[component],
        dependencies=[]
    )

    llm_workflow = LLMWorkflowMapper.to_llm_workflow(workflow)

    assert llm_workflow.name == workflow.name
    assert llm_workflow.description == workflow.description
    assert len(llm_workflow.components) == 1
    assert llm_workflow.components[0].identifier == "comp1"


def test_to_llm_dependency():
    dependency = ComponentDependency(component_input_key="inputX", source_label="comp1", target_label="comp2")

    llm_dependency = LLMWorkflowMapper._to_llm_dependency(dependency)

    assert llm_dependency.source == "comp1"
    assert llm_dependency.target == "comp2"
    assert llm_dependency.target_input == "inputX"
