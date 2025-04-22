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
        component_labels = { component.label for component in components }
        dependencies = []
        for llm_dependency in llm_workflow.dependencies:
            dependency = self._to_dependency(llm_dependency)
            # Skip dependencies that are not in the component list
            if dependency.source_label not in component_labels or dependency.target_label not in component_labels:
                continue
            dependencies.append(dependency)
        workflow.dependencies = dependencies
        workflow.auto_component_position()
        return workflow

    def _to_component(self, llm_component: LLMComponentModel, workflow_id: str):
        try:
            component: ComponentModel = self._component_library_index[llm_component.name]
        except KeyError:
            # Fallback to python coder
            component: ComponentModel = self._component_library_index['PythonCoder']
        component.label = llm_component.identifier
        component.workflow_id = workflow_id
        for component_input in component.inputs:
            llm_component_input = next((llm_component_input for llm_component_input in llm_component.inputs if llm_component_input.input_name == component_input.key), None)
            if llm_component_input:
                try:
                    component_input.value = llm_component_input.input_value
                except ValueError:
                    pass
                template_variables = {}
                for llm_template_variable in llm_component_input.template_variables:
                    template_variables[component_input.key+"."+llm_template_variable.template_variable_name] = llm_template_variable.template_variable_value
                component_input.template_variables = template_variables

        return component

    @staticmethod
    def _to_dependency(llm_dependency: LLMDependencyModel):
        template_variable_key = None
        if llm_dependency.target_input and llm_dependency.target_template_variable_name:
            template_variable_key = llm_dependency.target_input+"."+llm_dependency.target_template_variable_name
        dependency = ComponentDependency(
            component_input_key=llm_dependency.target_input,
            source_label=llm_dependency.source,
            target_label=llm_dependency.target,
            template_variable_key=template_variable_key
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

if __name__ == "__main__":
    llm_workflow = LLMWorkflowModel(
        name='PDF Table to LaTeX Agent',
        description='Reads a PDF file, extracts all tables and converts them to LaTeX, adding the title of the paper as a BibTeX reference.',
        components=[
            LLMComponentModel(
                name='FileToText',
                identifier='file_to_text',
                inputs=[
                    LLMComponentInput(
                        input_name='file_input',
                        input_value='path/to/file.pdf',
                        template_variables=[]
                    )
                ]
            ),
            LLMComponentModel(
                name='OpenAIPrompt',
                identifier='openai_prompt',
                inputs=[
                    LLMComponentInput(
                        input_name='system_prompt',
                        input_value='You are an agent that converts PDF content. Given the extracted text from a PDF of a research paper, extract all tables present in the document and convert each table to LaTeX format. Additionally, extract the title of the paper and generate a BibTeX reference entry using that title. Return your response as plain text.',
                        template_variables=[]
                    ),
                    LLMComponentInput(
                        input_name='user_prompt',
                        input_value='{{pdf_text}}',
                        template_variables=[
                            LLMTemplateVariable(
                                template_variable_name='pdf_text',
                                template_variable_value='file_to_text'
                            )
                        ]
                    )
                ]
            )
        ],
        undefined_components=[],
        dependencies=[
            LLMDependencyModel(
                source='file_to_text',
                target='openai_prompt',
                target_input='user_prompt',
                target_template_variable_name='pdf_text'
            )
        ]
    )
    mapper = LLMWorkflowMapper()
    workflow = mapper.to_workflow(llm_workflow)
