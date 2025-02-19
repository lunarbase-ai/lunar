# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from lunarbase import LUNAR_CONTEXT
from lunarbase.agent_copilot.llm_workflow_model import LLMComponentModel, LLMDependencyModel, LLMWorkflowModel, \
    LLMComponentInput, LLMTemplateVariable
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel, ComponentDependency


class LLMWorkflowMapper:
    def __init__(self):
        self._component_library_index = {
            registered_component.component_model.class_name: registered_component.component_model for registered_component in
            LUNAR_CONTEXT.lunar_registry.components
        }

    def to_workflow(self, llm_workflow: LLMWorkflowModel):
        workflow = WorkflowModel(
            name=llm_workflow.name,
            description=llm_workflow.description
        )
        components = []
        for llm_component in llm_workflow.components:
            components.append(self._to_component(llm_component, workflow.id))
        workflow.components = components
        dependencies = []
        for llm_dependency in llm_workflow.dependencies:
            dependencies.append(self._to_dependency(llm_dependency))
        workflow.dependencies = dependencies
        workflow.auto_component_position()
        return workflow

    def _to_component(self, llm_component: LLMComponentModel, workflow_id: str):
        component: ComponentModel = self._component_library_index[llm_component.name]
        component.label = llm_component.identifier
        component.workflow_id = workflow_id
        for component_input in component.inputs:
            llm_component_input = next((llm_component_input for llm_component_input in llm_component.inputs if llm_component_input.input_name == component_input.key), None)
            if llm_component_input:
                component_input.value = llm_component_input.input_value
                template_variables = {}
                for llm_template_variable in llm_component_input.template_variables:
                    template_variables[llm_template_variable.template_variable_name] = llm_template_variable.template_variable_value
                component_input.template_variables = template_variables

        return component

    @staticmethod
    def _to_dependency(llm_dependency: LLMDependencyModel):
        dependency = ComponentDependency(
            component_input_key=llm_dependency.target_input,
            source_label=llm_dependency.source,
            target_label=llm_dependency.target,
        )
        return dependency

    @staticmethod
    def to_llm_workflow(workflow: WorkflowModel):
        llm_workflow = LLMWorkflowModel(
            name=workflow.name,
            description=workflow.description,
            components=[]
        )
        llm_components = []
        for component in workflow.components:
            llm_components.append(LLMWorkflowMapper._to_llm_component(component))
        llm_workflow.components = llm_components
        llm_dependencies = []
        for dependency in workflow.dependencies:
            llm_dependencies.append(LLMWorkflowMapper._to_llm_dependency(dependency))
        llm_workflow.dependencies = llm_dependencies
        return llm_workflow

    @staticmethod
    def _to_llm_component(component: ComponentModel):
        llm_inputs = []
        for component_input in component.inputs:
            llm_template_variables = []
            for template_variable_name, template_variable_value in component_input.template_variables.items():
                llm_template_variables.append(LLMTemplateVariable(
                    template_variable_name=template_variable_name,
                    template_variable_value=template_variable_value
                ))
            llm_input = LLMComponentInput(
                input_name=component_input.key,
                input_value=str(component_input.value),
                template_variables=llm_template_variables
            )
            llm_inputs.append(llm_input)
        llm_component = LLMComponentModel(
            name=component.class_name,
            identifier=component.label,
            inputs=llm_inputs
        )
        return llm_component

    @staticmethod
    def _to_llm_dependency(dependency: ComponentDependency):
        llm_dependency = LLMDependencyModel(
            source=dependency.source_label,
            target=dependency.target_label,
            target_input=dependency.component_input_key,
            target_template_variable_name=dependency.template_variable_key
        )
        return llm_dependency

