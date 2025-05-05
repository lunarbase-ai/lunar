# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
from typing import Type

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import VectorStore
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models.base import BaseChatOpenAI

from lunarbase import LUNAR_CONTEXT
from lunarbase.agent_copilot.component_generator import ComponentGenerator
from lunarbase.agent_copilot.llm_workflow_mapper import LLMWorkflowMapper
from lunarbase.agent_copilot.llm_workflow_model import LLMWorkflowModel
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.utils import setup_logger

logger = setup_logger("workflow-copilot")

class AgentCopilot:

    LLM_EXAMPLES = ["""
    """]

    SYSTEM_PROMPT_TEMPLATE_NEW_WORKFLOW = """
    You are an expert workflow builder. You can use the components listed below to build a workflow. Do not make up components.
    If a component you need is not available, add it to undefined_components instead of components.

    AVAILABLE COMPONENTS:
    {{component_library}}
    
    EXAMPLES:
    {{examples}}
    """

    SYSTEM_PROMPT_TEMPLATE_WORKFLOW_MODIFICATION = """
    You are an expert workflow builder. Modify the following workflow according to the instruction.
    
    AVAILABLE COMPONENTS:
    {{component_library}}
    
    WORKFLOW:
    {{workflow}}
    """

    SYSTEM_PROMPT_DEPENDENCIES_TEMPLATE_WORKFLOW = """
    You are an expert workflow builder. Create the dependencies array for the following workflow. source_label and target_label
    must be valid existing identifiers of the workflow.
    
    WORKFLOW:
    {{workflow}}
    
    IDENTIFIERS:
    {{identifiers}}
    """

    def __init__(
        self,
        llm: BaseChatOpenAI,
        embeddings: OpenAIEmbeddings,
        vector_store: Type[VectorStore],
    ):
        self._client = llm
        self._client_embeddings = embeddings
        self._vector_store = vector_store
        self._component_library_index = {
            registered_component.component_model.name: registered_component.component_model for registered_component in
            LUNAR_CONTEXT.lunar_registry.components
        }
        self._component_generator = ComponentGenerator()

    def get_component_library_vectorstore(self):
        component_library = [
            component.view for component in LUNAR_CONTEXT.lunar_registry.components
        ]
        vectorstore = self._vector_store.from_texts(
            [component.description for component in component_library],
            embedding=self._client_embeddings,
            metadatas=[{"component": component} for component in component_library],
        )
        return vectorstore

    @staticmethod
    def _get_relevant_components(intent: str, vectorstore: VectorStore):
        retriever = vectorstore.as_retriever(search_kwargs={"k": 15})
        relevant_components = retriever.invoke(intent)
        return [document.metadata["component"].model_dump() for document in relevant_components]

    def get_system_prompt(self, intent: str):
        relevant_components = self._get_relevant_components(intent, self.get_component_library_vectorstore())
        system_prompt = PromptTemplate(
            input_variables=["component_library", "examples"],
            template=self.__class__.SYSTEM_PROMPT_TEMPLATE_NEW_WORKFLOW,
            template_format="jinja2",
        ).format(
            component_library=relevant_components, examples="\n".join(self.__class__.LLM_EXAMPLES)
        )
        return system_prompt

    def get_workflow_modification_system_prompt(self, workflow: LLMWorkflowModel, intent: str):
        relevant_components = self._get_relevant_components(intent, self.get_component_library_vectorstore())
        system_prompt = PromptTemplate(
            input_variables=["component_library", "workflow"],
            template=self.__class__.SYSTEM_PROMPT_TEMPLATE_WORKFLOW_MODIFICATION,
            template_format="jinja2",
        ).format(
            component_library=relevant_components, workflow=workflow
        )
        return system_prompt

    def get_dependencies_system_prompt(self, workflow: LLMWorkflowModel):
        system_prompt = PromptTemplate(
            input_variables=["workflow", "identifiers"],
            template=self.__class__.SYSTEM_PROMPT_DEPENDENCIES_TEMPLATE_WORKFLOW,
            template_format="jinja2",
        ).format(
            workflow=workflow,
            identifiers=[component.identifier for component in workflow.components]
        )
        return system_prompt

    def _invoke_structured_llm(self, schema, system_prompt, human_prompt):
        user_prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{{prompt}}",
            template_format="jinja2",
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt_template.format(prompt=human_prompt)),
        ]
        llm_output = self._client.with_structured_output(schema=schema, method="json_schema", include_raw=False).invoke(messages)
        return llm_output

    def generate_workflow(self, user_prompt: str):
        logger.info(f"Generating workflow for user prompt: {user_prompt}")
        system_prompt = self.get_system_prompt(user_prompt)
        llm_workflow_model = self._invoke_structured_llm(LLMWorkflowModel, system_prompt, user_prompt)
        for undefined_component in llm_workflow_model.undefined_components:
            logger.info(f"Generating component for undefined component: {undefined_component}")
            llm_workflow_model.components.append(
                self._component_generator.run(undefined_component.description, undefined_component.identifier)
            )
        llm_workflow_model.undefined_components.clear()
        # llm_workflow_model.dependencies = []
        # system_message = self.get_dependencies_system_prompt(llm_workflow_model)
        # workflow_dependencies = self._invoke_structured_llm(LLMDependencies, system_message, "Create the dependencies")
        # llm_workflow_model.dependencies = workflow_dependencies.dependencies
        logger.info(f"Generated workflow: {llm_workflow_model}")
        return LLMWorkflowMapper().to_workflow(llm_workflow_model)

    def modify_workflow(self, workflow: WorkflowModel, user_prompt: str):
        llm_workflow = LLMWorkflowMapper().to_llm_workflow(workflow)
        system_prompt = self.get_workflow_modification_system_prompt(llm_workflow, user_prompt)
        llm_modified_workflow = self._invoke_structured_llm(LLMWorkflowModel, system_prompt, user_prompt)
        for undefined_component in llm_modified_workflow.undefined_components:
            logger.info(f"Generating component for undefined component: {undefined_component}")
            llm_modified_workflow.components.append(
                self._component_generator.run(undefined_component.description, undefined_component.identifier)
            )
        logger.info(f"Modified workflow: {llm_modified_workflow}")
        return LLMWorkflowMapper().to_workflow(llm_modified_workflow)
