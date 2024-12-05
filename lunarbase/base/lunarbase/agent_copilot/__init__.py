from typing import Dict, Optional, Union

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from lunarbase import LUNAR_CONTEXT, LunarConfig
from lunarbase.modeling.llms import AzureChatGPT, LLM


class AgentCopilot:

    LLM_EXAMPLES = ["""
    Task description: Generate a workflow that takes the text "This is abracadabra" as input and outputs a list of words from the text.
    Expected output: {"workflow": [("TextInput", "qsKr4Vtd3d")], "components": {"TextInput": {"input": "This is abracadabra"}, "qsKr4Vtd3d": {"input": ["This", "is", "abracadabra"]}}, undefined_components": {"qsKr4Vtd3d": "A function that splits a given text into its constituent words."}} 
    """]

    SYSTEM_PROMPT_TEMPLATE_NEW_WORKFLOW = """
    You are a skilled AI engineer assistant that can generate workflows for solving user problems.
    A workflow is a direct acyclic graph with nodes represented by functions that perform specific steps in the workflow.
    
    The available components are given bellow in a JSON representation that includes their names, descriptions, expected inputs and output type.
    Each component returns exactly one output.
    
    For cases where components are not found in the given listing generate a small text description of the required sub-task - at most 100 tokens.
    Use random component identifiers of 10 characters as the name of such components.
    
    Your task is to split the user instruction into a set of sub-tasks, each one solvable by one component, and to generate the final workflow as a JSON of the following form:
    {"workflow": <a list of component name pairs denoting graph edges>, "components": {<component_name>: {<input_name>: <value or "undefined">}}, "undefined_components": <a dictionary of random component identifier to textual component description>}
    Undefined components should only contain the textual description of the sub-task for which there is not suitable existing component in the available components.
    Output only the JSON and nothing else.
    
    Use the examples below for guidance.
    
    AVAILABLE COMPONENTS:
    {{component_library}}
    
    EXAMPLES:
    {{examples}}
    
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

        component_library = [
            component.view for component in LUNAR_CONTEXT.lunar_registry.components
        ]

        self._system_prompt = PromptTemplate(
            input_variables=["component_library", "examples"],
            template=self.__class__.SYSTEM_PROMPT_TEMPLATE_NEW_WORKFLOW,
            template_format="jinja2",
        ).format(
            component_library=component_library, examples="\n".join(self.__class__.LLM_EXAMPLES)
        )

        llm = llm or AzureChatGPT(
            connection_attributes={
                "openai_api_version": self._config.AZURE_OPENAI_API_VERSION,
                "deployment_name": self._config.AZURE_OPENAI_DEPLOYMENT,
                "openai_api_key": self._config.AZURE_OPENAI_API_KEY,
                "azure_endpoint": self._config.AZURE_OPENAI_ENDPOINT,
                "model_name": self._config.AZURE_OPENAI_MODEL_NAME,
            }
        )

        self._client = AzureChatOpenAI(**llm.connection_attributes)

    def run(self, user_prompt: str):
        user_prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="{{prompt}}",
            template_format="jinja2",
        )

        system_message = SystemMessage(content=self._system_prompt)
        user_message = HumanMessage(
            content=user_prompt_template.format(prompt=user_prompt)
        )

        messages = [system_message, user_message]
        result = self._client.invoke(messages).content

        return str(result)


if __name__ == "__main__":
    # intent = "Generate a workflow that takes a text as input and outputs a version of that text with capitalised words."
    intent = "Generate a workflow that takes the text `Abracadabra` as input, waits for 10 seconds and then outputs the same text."

    copilot = AgentCopilot()
    result = copilot.run(intent)
    print(result)
