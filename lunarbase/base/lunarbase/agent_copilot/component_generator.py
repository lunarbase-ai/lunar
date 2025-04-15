# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from typing import Optional, Union, Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from lunarbase import LunarConfig, LUNAR_CONTEXT
from lunarbase.agent_copilot.llm_workflow_model import LLMComponentModel, LLMComponentInput, LLMTemplateVariable
from lunarbase.modeling.llms import LLM, AzureChatGPT

import re

from lunarbase.utils import setup_logger

logger = setup_logger("component-generator")


PARAMETER_REGEX = re.compile(r'(?<!{){([\w()]+)}(?!})')


def extract_template_variables(text: str):
    return {match: "" for match in PARAMETER_REGEX.findall(text)}


class ComponentGenerator:

    SYSTEM_PROMPT_NEW_COMPONENT = """Generate a python code that executes the users task. the inputs should be written
between {} and the output should be assigned to the variable `result`. Do not use external libraries. Your response must be only the code.
Do not wrap the code with any type of quotes.
    For example, if the task is to sum two numbers, the code should look like this:
    
    first_number = {first_number}
    second_number = {second_number}
    result = sum([first_number, second_number])
    
    """

    def __init__(
        self,
        llm: Optional[Union[LLM, Dict]] = None,
        config: Optional[Union[str, Dict, LunarConfig]] = None,
    ):
        self._config = config or LUNAR_CONTEXT.lunar_registry.config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self._system_prompt = PromptTemplate(
            input_variables=["component_library", "examples"],
            template=self.__class__.SYSTEM_PROMPT_NEW_COMPONENT,
            template_format="jinja2",
        ).format()

        llm = llm or AzureChatGPT(
            connection_attributes={
                "openai_api_version": self._config.AZURE_OPENAI_API_VERSION,
                "deployment_name": self._config.AZURE_OPENAI_DEPLOYMENT,
                "openai_api_key": self._config.AZURE_OPENAI_API_KEY,
                "azure_endpoint": self._config.AZURE_OPENAI_ENDPOINT,
                "model_name": self._config.AZURE_OPENAI_MODEL_NAME,
            }
        )

        self._client = AzureChatOpenAI(
            openai_api_version=llm.connection_attributes.openai_api_version,
            deployment_name=llm.connection_attributes.deployment_name,
            openai_api_key=llm.connection_attributes.openai_api_key,
            azure_endpoint=llm.connection_attributes.azure_endpoint,
            model_name=llm.connection_attributes.model_name,
        )

    def run(self, component_description: str, label: str):
        logger.info(f"Generating component for description: {component_description}")
        user_prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{{prompt}}",
            template_format="jinja2",
        )

        system_message = SystemMessage(content=self._system_prompt)
        user_message = HumanMessage(
            content=user_prompt_template.format(prompt=component_description)
        )

        client: AzureChatOpenAI = self._client

        messages = [system_message, user_message]
        llm_response = client.invoke(messages).content
        template_variables = extract_template_variables(llm_response)

        llm_template_variables = []
        for template_variable_name, template_variable_value in template_variables.items():
            llm_template_variables.append(LLMTemplateVariable(
                template_variable_name=template_variable_name,
                template_variable_value=template_variable_value
            ))

        python_coder_component = LLMComponentModel(
            name="PythonCoder",
            identifier=label,
            inputs=[LLMComponentInput(
                input_name="code",
                input_value=llm_response,
                template_variables=llm_template_variables
            )]
        )
        logger.info(f"Resulting component: {str(python_coder_component)}")
        return python_coder_component


if __name__ == "__main__":
    generator = ComponentGenerator()
    component = generator.run("Generate a component that takes a list of numbers and returns the sum of the numbers.", label="QwertY")
    print(component)
