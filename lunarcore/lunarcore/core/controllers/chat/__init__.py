import asyncio
import os.path
from types import FunctionType
from typing import Union, Dict, Any, Optional, List

from lunarcore.config import LunarConfig
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel, ComponentModel
from autogen import ConversableAgent, Cache

from lunarcore.core.typings.datatypes import DataType


def process_tool_name(tool_name: str):
    return tool_name.replace(" ", "_")

class WorkflowFunctionGenerator:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._workflow_controller = WorkflowController(config)
        self.workflow_output = {}

    def _post_process_workflow_output(self, workflow_output: Dict[str, Dict]):
        self.workflow_output = workflow_output
        tool_output = {}
        for component_label, component in workflow_output.items():
            component = ComponentModel.parse_obj(component)
            data_type = component.output.data_type

            if data_type == DataType.TEXT:
                tool_output[component_label] = component.output.value
            else:
                tool_output[component_label] = f'<lunartype type="{data_type.value}">{component_label}</lunartype>'
        return tool_output

    def _create_typed_function(
            self,
            name: str,
            workflow: WorkflowModel,
            params: set[tuple[Any, str, str, Union[str, None]]],
            user_id: Optional[str]
    ) -> FunctionType:
        param_str = ', '.join([f"{prefix.replace('-', '_')}__{param}__{template_var}: {ptype.__name__}" if template_var else f"{prefix.replace('-', '_')}__{param}: {ptype.__name__}" for ptype, prefix, param, template_var in params])
        params_set = '{' + ', '.join(
            [f"'{prefix.replace('-', '_')}__{param}__{template_var}':" + '{' + f"'0': {prefix.replace('-', '_')}__{param}__{template_var}, '1': '{prefix}', '2': '{param}', '3': '{template_var}'" + '}' if template_var else f"'{prefix.replace('-', '_')}__{param}':" + '{' + f"'0': {prefix.replace('-', '_')}__{param}, '1': '{prefix}', '2': '{param}', '3': None" + '}' for _, prefix, param, template_var in params]
        ) + '}'
        workflow_controller = self._workflow_controller
        post_process_workflow_output = self._post_process_workflow_output

        func_def = f"async def {name}({param_str}):\n" \
                   f"    params_set={params_set}\n" \
                   f"    for param_key, param in params_set.items():\n" \
                   f"        for component in workflow.components:\n" \
                   f"            if component.label == param['1']:\n"\
                   f"                input = next(iter([input for input in component.inputs if input.key==param['2']]), None)\n"\
                   f"                if param['3']:\n"\
                   f"                    input.template_variables[param['3']] = param['0']\n"\
                   f"                else:\n"\
                   f"                    input.value = param['0']\n"\
                   f"    run_output = await workflow_controller.run(workflow, user_id)\n" \
                   f"    return post_process_workflow_output(run_output)\n"

        local_namespace = {}
        global_definitions = globals()
        wf_definitions = {
            'workflow': workflow,
            'workflow_controller': workflow_controller,
            'post_process_workflow_output': post_process_workflow_output,
            'user_id': user_id
        }
        exec(func_def, {**global_definitions, **wf_definitions}, local_namespace)
        return local_namespace[name]

    def convert_workflow_to_function(self, workflow: WorkflowModel, user_id: Optional[str] = None):
        inputs_set = set()
        for component in workflow.components:
            for input in component.inputs:
                if input.value is None or \
                   input.value == "" or \
                   input.value == ":undef:" or \
                   input.data_type == DataType.LIST and input.value == []:
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
            input = next((inp for inp in component.inputs if inp.key == dependency.component_input_key))
            targets_set.add((input.data_type.type(), dependency.target_label, dependency.component_input_key, None))
        workflow_inputs = inputs_set - targets_set

        function = self._create_typed_function(
            name=process_tool_name(workflow.name),
            workflow=workflow,
            params=workflow_inputs,
            user_id=user_id
        )
        return function


class ChatController:

    CHAT_PATH_REFERENCE = "chat"

    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._workflow_controller = WorkflowController(config)

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
            human_input_mode="NEVER",
        )

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
            default_auto_reply="TERMINATE",
        )

        workflow_function_generator = WorkflowFunctionGenerator(self._config)

        for workflow in workflows:
            run_workflow = workflow_function_generator.convert_workflow_to_function(workflow, user_id)


            assistant.register_for_llm(
                name=process_tool_name(workflow.name),
                description=f"Workflow Description: {workflow.description[:1024]}\n\nNote: If the return is a <lunartype> tag, the tag can be added to the answer (exactly as it comes from the workflow execution), and it will be rendered properly."
            )(run_workflow)
            user_proxy.register_for_execution(name=process_tool_name(workflow.name))(run_workflow)

        with Cache.disk(cache_path_root=os.path.join(self._config.USER_DATA_PATH, user_id, self.CHAT_PATH_REFERENCE)) as cache:
            chat_result = await user_proxy.a_initiate_chat(assistant, message=human_message, cache=cache)

        return {"workflowOutput": workflow_function_generator.workflow_output, "chatResult": chat_result}


if __name__ == "__main__":
    config = LunarConfig.get_config(settings_file_path="/Users/danilomirandagusicuma/Developer/lunarbase/lunar/.env")
    chat_controller = ChatController(config)
    workflow_controller = WorkflowController(config)
    workflow: WorkflowModel = asyncio.run(workflow_controller.get_by_id("50372a82-3588-40d6-b50a-ad1f4d21dc59", "danilo.m.gusicuma@gmail.com"))
    # response = chat_controller.initiate_workflow_chat("Give me interesting information about tigers from wikipedia", workflow, "admin")
    func = chat_controller.convert_workflow_to_function(workflow)
    response = asyncio.run(func(["AAPL"]))
    print(response)
