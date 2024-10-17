import asyncio
import os.path
from types import FunctionType
from typing import Union, Dict, Any, Optional, List

from lunarcore import LunarConfig, get_config
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel
from autogen import ConversableAgent, Cache

from lunarcore.core.typings.datatypes import DataType


def process_tool_name(tool_name: str):
    return tool_name.replace(" ", "_")


class ChatController:

    CHAT_PATH_REFERENCE = "chat"

    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._workflow_controller = WorkflowController(config)

    def create_typed_function(
            self,
            name: str,
            workflow: WorkflowModel,
            params: set[tuple[Any, str, str, Union[str, None]]],
            user_id: Optional[str]
    ) -> FunctionType:
        param_str = ', '.join([f"{prefix.replace('-', '_')}__{param}__{template_var}: {ptype.__name__}" if template_var else f"{prefix.replace('-', '_')}__{param}: {ptype.__name__}" for ptype, prefix, param, template_var in params])
        params_set = '{' + ', '.join(
            [f"({prefix.replace('-', '_')}__{param}__{template_var}, '{prefix}', '{param}', '{template_var}')" if template_var else f"({prefix.replace('-', '_')}__{param}, '{prefix}', '{param}', None)" for _, prefix, param, template_var in params]
        ) + '}'
        workflow_controller=self._workflow_controller

        func_def = f"async def {name}({param_str}):\n" \
                   f"    params_set={params_set}\n" \
                   f"    for param in params_set:\n" \
                   f"        for component in workflow.components:\n" \
                   f"            if component.label == param[1]:\n"\
                   f"                input = next((input for input in component.inputs if input.key==param[2]), None)\n"\
                   f"                if param[3]:\n"\
                   f"                    input.template_variables[param[3]] = param[0]\n"\
                   f"                else:\n"\
                   f"                    input.value = param[0]\n"\
                   f"    return await workflow_controller.run(workflow, user_id)"

        local_namespace = {}
        global_definitions = globals()
        wf_definitions = {
            'workflow': workflow,
            'workflow_controller': workflow_controller,
            'user_id': user_id
        }
        exec(func_def, {**global_definitions, **wf_definitions}, local_namespace)
        return local_namespace[name]

    def convert_workflow_to_function(self, workflow: WorkflowModel, user_id: Optional[str] = None):
        inputs_set = set()
        for component in workflow.components:
            for input in component.inputs:
                if input.value is None or input.value == "" or input.value == ":undef:":
                    inputs_set.add((input.data_type.type(), component.label, input.key, None))
                for key, value in input.template_variables.items():
                    if value is None or value == "" or value == ":undef:":
                        inputs_set.add((DataType.TEXT.type(), component.label, input.key, key))

        targets_set = set()
        for dependency in workflow.dependencies:
            if dependency.template_variable_key:
                targets_set.add((
                    DataType.TEXT.type(),
                    dependency.target_label,
                    dependency.component_input_key,
                    dependency.template_variable_key
                ))
                continue
            component = next((component for component in workflow.components if component.label == dependency.target_label))
            input = next((input for input in component.inputs if input.key == dependency.component_input_key))
            targets_set.add((input.data_type.type(), dependency.target_label, dependency.component_input_key, None))
        workflow_inputs = inputs_set - targets_set

        function = self.create_typed_function(
            name=process_tool_name(workflow.name),
            workflow=workflow,
            params=workflow_inputs,
            user_id=user_id
        )
        return function

    async def initiate_workflow_chat(self, human_message, workflow_ids: List[str], user_id: str):

        workflows = []
        for workflow_id in workflow_ids:
            workflows.append(await self._workflow_controller.get_by_id(workflow_id=workflow_id, user_id=user_id))

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

        for workflow in workflows:
            run_workflow = self.convert_workflow_to_function(workflow, user_id)

            assistant.register_for_llm(
                name=process_tool_name(workflow.name),
                description=workflow.description[:1024]
            )(run_workflow)
            user_proxy.register_for_execution(name=process_tool_name(workflow.name))(run_workflow)

        with Cache.disk(cache_path_root=os.path.join(self._config.USER_DATA_PATH, user_id, self.CHAT_PATH_REFERENCE)) as cache:
            chat_response = await user_proxy.a_initiate_chat(assistant, message=human_message, cache=cache)

        return chat_response


# if __name__ == "__main__":
    # config = get_config(settings_file_path="/Users/danilomirandagusicuma/Developer/lunarbase/lunar/.env")
    # chat_controller = ChatController(config)
    # workflow_controller = WorkflowController(config)
    # workflow: WorkflowModel = asyncio.run(workflow_controller.get_by_id("78274f9e-2d4c-4edd-af32-f89f32aa331d", "admin"))
    # response = chat_controller.initiate_workflow_chat("Give me interesting information about tigers from wikipedia", workflow, "admin")
    # func = chat_controller.convert_workflow_to_function(workflow)
    # # response = asyncio.run(func("Give me interesting information about tigers from wikipedia"))
    # print(response)
