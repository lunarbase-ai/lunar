import asyncio
from typing import Union, Dict

from lunarcore import LunarConfig, get_config
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel
from autogen import ConversableAgent

from lunarcore.core.typings.datatypes import DataType


class ChatController:

    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._workflow_controller = WorkflowController(config)

    def convert_workflow_to_function(self, workflow: WorkflowModel):
        inputs_set = set()
        for component in workflow.components:
            for input in component.inputs:
                if input.value is None or input.value == "" or input.value == ":undef:":
                    inputs_set.add((component.label, input.key, input.data_type))
                for key, value in input.template_variables.items():
                    if value is None or value == "" or value == ":undef:":
                        inputs_set.add((component.label, input.key, key, DataType.TEXT))

        targets_set = set()
        for dependency in workflow.dependencies:
            if dependency.template_variable_key:
                targets_set.add((
                    dependency.target_label,
                    dependency.component_input_key,
                    dependency.template_variable_key,
                    DataType.TEXT
                ))
            targets_set.add((dependency.target_label, dependency.component_input_key, DataType.TEXT))
        workflow_inputs = inputs_set - targets_set
        return workflow_inputs

    def process_tool_name(self, tool_name: str):
        return tool_name.replace(" ", "_")

    def initiate_workflow_chat(self, human_message, workflow: WorkflowModel, user_id: str):
        assistant = ConversableAgent(
            name="Assistant",
            system_message="You are a helpful AI assistant. "
                           "Return 'TERMINATE' when the task is done.",
            llm_config={"config_list": [{
                "model": self._config.AZURE_DEPLOYMENT,
                "api_type": "azure",
                "api_key": self._config.OPENAI_API_KEY,
                "base_url": self._config.AZURE_ENDPOINT,
                "api_version": self._config.OPENAI_API_VERSION
            }]},
        )

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
        )

        async def run_workflow() -> Dict:
            return await self._workflow_controller.run(workflow, user_id)

        assistant.register_for_llm(
            name=self.process_tool_name(workflow.name),
            description=workflow.description
        )(run_workflow)
        user_proxy.register_for_execution(name=self.process_tool_name(workflow.name))(run_workflow)

        return user_proxy.initiate_chat(assistant, message=human_message)


if __name__ == "__main__":
    config = get_config(settings_file_path="/Users/danilomirandagusicuma/Developer/lunarbase/lunar/.env")
    chat_controller = ChatController(config)
    workflow_controller = WorkflowController(config)
    workflow: WorkflowModel = asyncio.run(workflow_controller.get_by_id("78274f9e-2d4c-4edd-af32-f89f32aa331d", "admin"))
    # response = chat_controller.initiate_workflow_chat("Generate a random number", workflow, "admin")
    response = chat_controller.convert_workflow_to_function(workflow)
    print(response)
