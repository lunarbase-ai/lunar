# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import inspect
import json
import os
import random
import regex
import warnings

from langchain.prompts.prompt import PromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Union

from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.data_models import (
    ComponentDependency,
    ComponentInput,
    ComponentModel,
    ComponentOutput,
    WorkflowModel,
)
from lunarcore.core.typings.datatypes import File
from lunarcore.errors import LLMResponseError
from lunarcore.utils import get_file_content, setup_logger

from lunarcore.core.auto_workflow.config import (
    PATTERN_JSON,
    PATTERN_DEF_FUNC,
    PATTERN_DEF_TYPES,
    PATTERN_LLM_ANS_PYTHON,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    OPENAI_API_TYPE,
    OPENAI_API_VERSION,
    OPENAI_DEPLOYMENT_NAME,
    OPENAI_MODEL_KWARGS,
    OPENAI_API_KEY_ENV,
    AZURE_ENDPOINT_ENV,
    COMPONENT_INPUTS_POSTPROCESS,
    TEMPLATE_VARIABLE_KEY_PREFIX,
    TEMPLATE_VARIABLE_KEY_TEMPLATE,
    COMPONENT_LABEL_PREFIX,
    MISSED_PROPERTY_GETTER_PATTERN,
    COMPONENT_SOURCE_REPR,
    TEMPLATE_VARIABLE_REPR,
    PROMPT_FILE_TEMPLATE,
    PROMPT_NO_FILES_REPR,
    EXAMPLE_WORKFLOWS_DIR,
    RELEVANT_INTENTS_PROMPT_TEMPLATE,
    RELEVANT_COMPONENTS_EXAMPLE_TEMPLATE,
    WORKFLOW_PROMPT_EXAMPLE_TEMPLATE,
    WORKFLOW_MODIFICATION_PROMPT_EXAMPLE_TEMPLATE,
    WORKFLOW_MODIFICATION_PROMPT_WORKFLOW_EXAMPLE_TEMPLATE,
    COMPONENT_PROMPT_EXAMPLE_TEMPLATE,
    MAX_NR_EXAMPLES,
    MAX_NR_EXTRA_EXAMPLES,
    NR_INTENT_EXAMPLES,
)

from lunarcore.core.auto_workflow.default_factories import (
    prompt_data_default,
    relevant_components_prompt_template_default,
    relevant_intents_prompt_template_default,
    workflow_prompt_template_default,
    workflow_modification_prompt_template_default,
    component_prompt_template_default,
)

logger = setup_logger("workflow-copilot")


class AutoWorkflow(BaseModel):
    """
    AutoWorkflow uses GPT 3.5 API to set up a workflow of components
    automatically, given an instruction inputted by the user.
    """

    workflow: WorkflowModel = Field(default=...)
    azure_endpoint: str = Field(
        default_factory=lambda: os.environ.get(AZURE_ENDPOINT_ENV, "")
    )
    openai_api_key: str = Field(
        default_factory=lambda: os.environ.get(OPENAI_API_KEY_ENV, "")
    )
    prompt_data: Dict = Field(default_factory=prompt_data_default)
    files: Dict[str, File] = Field(default_factory=dict)
    relevant_intents_prompt_template: PromptTemplate = Field(
        default_factory=relevant_intents_prompt_template_default
    )
    relevant_components_prompt_template: PromptTemplate = Field(
        default_factory=relevant_components_prompt_template_default
    )
    workflow_prompt_template: PromptTemplate = Field(
        default_factory=workflow_prompt_template_default
    )
    workflow_modification_prompt_template: PromptTemplate = Field(
        default_factory=workflow_modification_prompt_template_default
    )
    component_prompt_template: PromptTemplate = Field(
        default_factory=component_prompt_template_default
    )
    example2components: Dict[str, List[str]] = Field(default_factory=dict)
    component2examples: Dict[str, Dict] = Field(default_factory=dict)
    intent2example: Dict[str, Dict] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.example2components and not self.component2examples:
            self._build_component_example_maps()
        if not self.intent2example:
            self._build_intent_example_map()

    def _build_component_example_maps(self):
        self._append_component_example_maps(default=True)
        self._append_component_example_maps(default=False)

    def _append_component_example_maps(self, default: bool = False):
        prompt_data_key = (
            "example_workflows_default"
            if default
            else "example_workflows_prompt_dependent"
        )
        for example in self.prompt_data[prompt_data_key]:
            workflow_filename = example["answer_workflow_file"]
            workflow = self._file2workflow(workflow_filename)
            components = set(
                self._workflow2components(workflow)
            )  # converting to set to remove same components
            for component_name in components:
                if component_name in self.component2examples:
                    self.component2examples[component_name].append(example)
                else:
                    self.component2examples[component_name] = [example]
            self.example2components[workflow_filename] = components

    def _workflow2components(self, workflow: WorkflowModel):
        components = [c.class_name for c in workflow.components]
        return components

    def _component2example_files(self):
        component_example_files = {}
        for component_model in COMPONENT_REGISTRY.components.values():
            component_name = component_model.class_name
            component_example_files[component_name] = []
            if component_name in self.component2examples:
                for example in self.component2examples[component_name]:
                    example_file = example["answer_workflow_file"]
                    component_example_files[component_name].append(example_file)
        return component_example_files

    def _component2example_files_str(self):
        component_example_files = self._component2example_files()
        sb = []
        for component_name, component_files in component_example_files.items():
            sb.append(f"{component_name}: {component_files}")
        return "\n".join(sb)

    def _build_intent_example_map(self):
        for prompt_data_key in (
            "example_workflows_default",
            "example_workflows_prompt_dependent",
        ):
            for example in self.prompt_data[prompt_data_key]:
                self.intent2example[example["description"]] = example

    def _create_client(self):
        client = AzureChatOpenAI(
            model_name=OPENAI_MODEL_NAME,
            temperature=OPENAI_TEMPERATURE,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_version=OPENAI_API_VERSION,
            deployment_name=OPENAI_DEPLOYMENT_NAME,
            openai_api_key=OPENAI_API_KEY_ENV,
            azure_endpoint=AZURE_ENDPOINT_ENV,
            model_kwargs=OPENAI_MODEL_KWARGS,
        )
        return client

    def _add_files(self, files: List[File]):
        for file in files:
            self.files[file.path] = file

    @staticmethod
    def _input_labels(ips: Union[List, ComponentInput]):
        if not isinstance(ips, list):
            ips = [ips]
        return [ip.key for ip in ips]

    @staticmethod
    def _input_labels_str(ips: Union[List, ComponentInput]):
        return ", ".join([f'"{ip}"' for ip in AutoWorkflow._input_labels(ips)])

    @staticmethod
    def components_str():
        sb = ["######## COMPONENT REGISTRY ########\n"]
        for component_model in COMPONENT_REGISTRY.components.values():
            sb.append(f"{component_model.class_name}")
            sb.append(f"Component description: {component_model.description}")
            sb.append(
                f"Input labels: {AutoWorkflow._input_labels_str(component_model.inputs)}"
            )
            sb.append("")
        sb.append("################")
        return "\n".join(sb)

    def _component_description(self, component_name: str):
        package_component_tuple = COMPONENT_REGISTRY.get_by_class_name(component_name)
        if package_component_tuple:
            _, component_model = package_component_tuple
            return component_model.description
        return None

    def _validate_example_workflow(self, workflow: WorkflowModel):
        if not workflow.description:
            warnings.warn(f"Example workflow '{workflow.name}' misses a description.")
        for component in workflow.components:
            if not component.description and not COMPONENT_REGISTRY.get_by_class_name(
                component.class_name
            ):
                warnings.warn(
                    f"Component '{component.name}' in example workflow '{workflow.name}' misses a description."
                )

    def _prompt_example_files(self, example: Dict):
        file_objects = []
        files = example.get("files", [])
        for file in files:
            file_object = File(path=file["path"], description=file["description"])
            file_objects.append(file_object)
        return file_objects

    def _relevant_components_examples_str(
        self, example_template: str = RELEVANT_COMPONENTS_EXAMPLE_TEMPLATE
    ):
        examples = self.prompt_data["example_relevant_components"]
        sb = []
        for example in examples:
            sb.append(
                example_template.format(
                    description=example["description"], answer=example["answer"]
                )
            )
        return "\n".join(sb)

    def _choose_examples_generation(
        self,
        description: str,
        nr_intent_examples: int = NR_INTENT_EXAMPLES,
        max_nr_examples: int = MAX_NR_EXAMPLES,
        max_nr_extra: int = MAX_NR_EXTRA_EXAMPLES,
    ):
        logger.debug(
            f"Asking LLM for relevant components to the following workflow "
            f"intent/description:\n{description}"
        )
        relevant_components = self._openai_quest_relevant_components(description)
        logger.debug(
            f"Got the following relevant components LLM answer:\n{relevant_components}\n"
        )
        component2score = {
            c: i + 1 for i, c in enumerate(relevant_components[::-1])
        }  # higher score ==> more relevant
        components_left = set(relevant_components)
        examples = []

        # Add default examples
        for example in self.prompt_data["example_workflows_default"]:
            workflow_filename = example["answer_workflow_file"]
            for component in self.example2components[workflow_filename]:
                if component in components_left:
                    components_left.remove(component)
            examples.append(example)

        # Add most example with most similar intent
        logger.debug(
            f"Asking LLM for relevant intents to the following workflow "
            f"intent/description:\n{description}"
        )
        relevant_intents = self._openai_quest_relevant_intents(
            description, nr_intent_examples
        )
        logger.debug(
            f"Got the following relevant intents LLM answer:\n{relevant_intents}\n"
        )
        for intent in relevant_intents:
            if intent in self.intent2example:
                example = self.intent2example[intent]
                if example not in examples:
                    examples.append(example)
                    for component in self.example2components[
                        example["answer_workflow_file"]
                    ]:
                        if component in components_left:
                            components_left.remove(component)
            else:
                warnings.warn(
                    f"Could not find an example with the intent '{intent}'. Skipping!"
                )

        # Add examples with relevant components
        for component in relevant_components:
            if len(examples) >= max_nr_examples:
                break
            if component in components_left and component in self.component2examples:
                best_example = None
                best_score = 0
                best_example_components = []
                for example in self.component2examples[component]:
                    score = 0
                    workflow_filename = example["answer_workflow_file"]
                    example_components = self.example2components[workflow_filename]
                    for example_component in example_components:
                        if example_component in components_left:
                            score += component2score[example_component]
                    if score > best_score:
                        best_example = example
                        best_score = score
                        best_example_components = example_components
                if best_example:
                    examples.append(best_example)
                    for example_component in best_example_components:
                        if example_component in components_left:
                            components_left.remove(example_component)

        # Add extra examples with relevant components (until upper limit is reached)
        extra_examples = []
        for component in relevant_components:
            if component in self.component2examples:
                extra_examples += self.component2examples[component]
        random.shuffle(extra_examples)
        nr_extra = 0
        for example in extra_examples:
            if len(examples) >= max_nr_examples or nr_extra >= max_nr_extra:
                break
            if example in examples:
                continue
            examples.append(example)
            nr_extra += 1

        logger.debug(
            f"Returning the following examples to use in the few-shot prompt:\n"
            f'{", ".join([ex["answer_workflow_file"] for ex in examples])}'
        )

        return examples

    def _workflow_examples_str_generation(
        self,
        description,
        example_template: str = WORKFLOW_PROMPT_EXAMPLE_TEMPLATE,
    ):
        examples = self._choose_examples_generation(description)
        sb = []
        for example in examples:
            answer_workflow = self._workflow_file_llm_repr_str(
                example["answer_workflow_file"]
            )
            sb.append(
                example_template.format(
                    description=example["task"],
                    files=self._files2prompt(self._prompt_example_files(example)),
                    workflow_llm_repr=answer_workflow,
                )
            )
        return "\n".join(sb)

    def _workflow_examples_str_modification(  # TODO: select relevant components as above
        self,
        instruction: str,
        example_template: str = WORKFLOW_PROMPT_EXAMPLE_TEMPLATE,
        task_format: bool = True,
    ):
        # examples = self.prompt_data['example_workflows_default']
        examples = self._choose_examples_generation(instruction)
        sb = []
        task_key = "task" if task_format else "description"
        for example in examples:
            answer_workflow = self._workflow_file_llm_repr_str(
                example["answer_workflow_file"]
            )
            sb.append(
                example_template.format(
                    description=example[task_key],
                    files=self._files2prompt(self._prompt_example_files(example)),
                    workflow_llm_repr=answer_workflow,
                )
            )
        return "\n".join(sb)

    def _file2workflow(self, file_name: str, dir_name: str = EXAMPLE_WORKFLOWS_DIR):
        path = os.path.join(os.path.dirname(__file__), dir_name, file_name)
        workflow_json_str = get_file_content(path)
        workflow_model = WorkflowModel.parse_raw(workflow_json_str)
        return workflow_model

    def _workflow_file_llm_repr_str(
        self, file_name: str, dir_name: str = EXAMPLE_WORKFLOWS_DIR
    ):
        workflow_model = self._file2workflow(file_name, dir_name)
        self._validate_example_workflow(workflow_model)
        workflow_repr_str = self._workflow_llm_repr_str(workflow_model)
        return workflow_repr_str

    def _workflow_modification_examples_str(self):
        examples = self.prompt_data["example_workflow_modifications"]
        sb = []
        for example in examples:
            initial_workflow = self._workflow_file_llm_repr_str(
                example["initial_workflow_file"]
            )
            answer_workflow = self._workflow_file_llm_repr_str(
                example["answer_workflow_file"]
            )
            sb.append(
                WORKFLOW_MODIFICATION_PROMPT_EXAMPLE_TEMPLATE.format(
                    task=json.dumps(example["task"]),
                    initial_workflow_llm_repr=initial_workflow,
                    answer_workflow_llm_repr=answer_workflow,
                )
            )
        return "\n".join(sb)

    def _remove_llm_ans_python_formatting(self, code):
        cleaned_code = regex.sub(
            PATTERN_LLM_ANS_PYTHON, r"\1", code, flags=regex.DOTALL
        )
        return cleaned_code

    def _remove_def_types(self, code: str):
        for def_part, _, _ in regex.findall(PATTERN_DEF_FUNC, code, regex.DOTALL):
            def_part_wo_types = regex.sub(PATTERN_DEF_TYPES, "", def_part)
            code = code.replace(def_part, def_part_wo_types)
        return code

    def _postprocess_custom_component_code(self, code):
        code = self._remove_llm_ans_python_formatting(code)
        # code = self._remove_def_types(code)
        return code

    def _get_class_methods(
        self, package_name: str, class_name: str, import_functions: List[str] = ["run"]
    ):
        _, component = COMPONENT_REGISTRY.get_by_class_name(class_name)
        module_path = component.component_code
        module_code = get_file_content(module_path)
        code_sb = []
        for function_name in import_functions:
            try:
                module = compile(module_code, module_path, "exec")
                exec(module)
                cls = globals()[class_name]
                function_source = inspect.getsource(getattr(cls, function_name))
                code_sb.append(function_source)
            except (IOError, TypeError, IndexError, AttributeError):
                warnings.warn(
                    f"Failed to retrieve source code of function "
                    f"'{function_name}' in class '{class_name}'. Skipping it!"
                )
        code = "\n".join(code_sb)
        return code

    def _component_example_values(self, example: dict):
        description = example.get("description", "")
        input_labels = example.get("input_labels", "")
        code = example.get("code", "").format(
            inputs_postprocess=COMPONENT_INPUTS_POSTPROCESS
        )
        class_name = example.get("name", "")
        if class_name:
            package_component_tuple = COMPONENT_REGISTRY.get_by_class_name(class_name)
            if package_component_tuple:
                package_name, component = package_component_tuple
                description = description or component.description
                input_labels = input_labels or [
                    component_input.key for component_input in component.inputs
                ]
                if not code:
                    code = self._get_class_methods(
                        package_name,
                        class_name,
                        example.get("import_functions", ["run"]),
                    )
                    warnings.warn(
                        f"Could not find provided code of class '{class_name}' in "
                        f"package '{package_name}'. Copied the source code, but not "
                        f"recommended to use as an example."
                    )
        return class_name, description, input_labels, code

    def _components_examples_str(self):
        example_components = self.prompt_data["example_components"]
        sb = []
        for example in example_components:
            name, description, input_labels, code = self._component_example_values(
                example
            )
            # code = self._remove_def_types(code)
            if description and input_labels and code:
                sb.append(
                    COMPONENT_PROMPT_EXAMPLE_TEMPLATE.format(
                        description=description, input_labels=input_labels, code=code
                    )
                )
            else:
                warnings.warn(
                    f"Code example with name '{name or 'NAME MISSING'}' "
                    f"was skipped since it was not found"
                )
        return "\n".join(sb)

    def _llm_str2json(self, llm_str: str):
        try:
            json_str = regex.findall(PATTERN_JSON, llm_str)[
                0
            ]  # simple error fix if LLM prints more thant {}
        except:
            try:  # try adding missing or removing extra '}' in end
                llm_str = llm_str[: max(llm_str.rfind("}") + 1, llm_str.rfind("]") + 1)]
                while llm_str.count("{") > llm_str.count("}"):
                    llm_str = llm_str + "}"
                json_str = regex.findall(PATTERN_JSON, llm_str)[0]
            except:
                raise LLMResponseError("Could not parse LLM response to JSON")
        return json.loads(json_str)

    def _try_value2component(self, value: Any):
        if isinstance(value, str):
            return value.replace("[", "").replace("]", "")
        return value

    def _get_componentinput_by_label(
        self, input_label: str, component_inputs: List[ComponentInput]
    ):
        for component_input in component_inputs:
            if component_input.key == input_label:
                return component_input
        return None

    def _add_template_variable_dependencies(
        self,
        template_variable_data: Dict[str, Any],
        input_label: str,
        id2component: Dict[str, ComponentModel],
        target_component: str,
        component_input: ComponentInput,
        dependencies: List[ComponentDependency],
    ):
        for template_variable, variable_value in template_variable_data.items():
            template_variable_label = TEMPLATE_VARIABLE_KEY_TEMPLATE.format(
                label=input_label, variable=template_variable
            )
            source_candidate = self._try_value2component(variable_value)
            if source_candidate in id2component:
                d = ComponentDependency(
                    component_input_key=input_label,
                    source_label=id2component[source_candidate].label,
                    target_label=id2component[target_component].label,
                    template_variable_key=template_variable_label,
                )
                dependencies.append(d)
            else:
                component_input.template_variables[
                    template_variable_label
                ] = variable_value
        return dependencies

    def _add_user_component_input(
        self,
        id2component: Dict[str, ComponentModel],
        target_component: str,
        input_label: str,
        input_value: Any,
        input_data: Dict[str, Any],
        dependencies: List[ComponentDependency],
    ):
        component_input = self._get_componentinput_by_label(
            input_label,
            id2component[target_component].inputs,
        )
        if component_input:
            component_input.value = input_value
            if "template_variables" in input_data:
                self._add_template_variable_dependencies(
                    input_data["template_variables"],
                    input_label,
                    id2component,
                    target_component,
                    component_input,
                    dependencies,
                )
        else:
            warnings.warn(
                f"Could not find input label '{input_label}' "
                f"of component {target_component}. Skipping!"
            )

    def _add_component_inputs(self, llm_repr: Dict, id2component: Dict):
        dependencies = []
        for target_component, target_component_data in llm_repr.items():
            for input_label, input_data in target_component_data[
                "input_labels"
            ].items():
                input_value = input_data["value"]
                source_candidate = self._try_value2component(input_value)
                if (
                    isinstance(source_candidate, str)
                    and source_candidate in id2component
                ):
                    d = ComponentDependency(
                        component_input_key=input_label,
                        source_label=id2component[source_candidate].label,
                        target_label=id2component[target_component].label,
                    )
                    dependencies.append(d)
                else:  # then input sorce is assummed to be manual user input
                    self._add_user_component_input(
                        id2component,
                        target_component,
                        input_label,
                        input_value,
                        input_data,
                        dependencies,
                    )
        return dependencies

    def _create_component_by_classname(
        self,
        name: str = "PlaceHolder",
        description: str = "",
        input_labels: Dict[str, Dict] = None,
        label: str = None,
    ):
        package_component_tuple = COMPONENT_REGISTRY.get_by_class_name(name)
        if package_component_tuple:
            register_component = package_component_tuple[1]
            component_class_path = os.path.join(
                COMPONENT_REGISTRY.registry_root,
                os.path.dirname(register_component.component_code),
            )
            component = COMPONENT_REGISTRY.generate_component_model(
                component_class_path
            )
            component.id = register_component.id
        else:
            component = self.generate_custom_component(
                name, description, list(input_labels)
            )
        if label:
            component.label = label
        return component

    def _files2prompt(self, files: List[File]):
        if files:
            file_rows = []
            for file in files:
                file_row = PROMPT_FILE_TEMPLATE.format(
                    description=file.description, path=file.path
                )
                file_rows.append(file_row)
            return "\n".join(file_rows)
        return PROMPT_NO_FILES_REPR

    def _template_variables_relevant_intents_prompt(
        self, description: str, nr_intent_examples: int = NR_INTENT_EXAMPLES
    ):
        template_variables = {
            "example_intents": "\n".join(self.intent2example),
            "nr_relevant_intent_examples": nr_intent_examples,
            "intent": description,
        }
        return template_variables

    def _template_variables_relevant_components_prompt(self, description: str):
        template_variables = {
            "components": self.components_str(),
            "examples": self._relevant_components_examples_str(),
            "description": description,
        }
        return template_variables

    def _template_variables_workflow_prompt(self, task: str):
        template_variables = {
            "components": self.components_str(),
            "examples": self._workflow_examples_str_generation(task),
            "task": task,  # TODO: Security issue -- user can input extra instructions...
            "files": self._files2prompt(list(self.files.values())),
        }
        return template_variables

    def _template_variables_workflow_modification_prompt(self, instruction: str):
        template_variables = {
            "components": self.components_str(),
            "workflow_examples": self._workflow_examples_str_modification(
                instruction,
                WORKFLOW_MODIFICATION_PROMPT_WORKFLOW_EXAMPLE_TEMPLATE,
                task_format=False,
            ),
            "modification_examples": self._workflow_modification_examples_str(),
            "instruction": instruction,  # TODO: Security issue -- user can input extra instructions...
            "workflow": self._workflow_llm_repr_str(),
        }
        return template_variables

    def _template_variables_component_prompt(
        self, description: str, input_labels: List
    ):
        template_variables = {
            "examples": self._components_examples_str(),
            "description": description,
            "input_labels": input_labels,
        }
        return template_variables

    def _openai_quest(self, prompt_template: PromptTemplate, template_variables: Dict):
        client = self._create_client()
        chain = prompt_template | client
        # print(prompt_template.format(**template_variables))  # TODO: remove this
        # input()
        chain_results = chain.invoke(template_variables)
        result_text = chain_results.content
        return result_text  # .strip('\n').strip()

    def _openai_quest_relevant_intents(
        self, description: str, nr_intent_examples: int = NR_INTENT_EXAMPLES
    ):
        template_variables = self._template_variables_relevant_intents_prompt(
            description, nr_intent_examples
        )  # TODO
        llm_ans = self._openai_quest(
            self.relevant_intents_prompt_template, template_variables
        )
        relevant_intents = llm_ans.split("\n")
        return relevant_intents

    def _openai_quest_relevant_components(self, description: str):
        template_variables = self._template_variables_relevant_components_prompt(
            description
        )
        llm_ans = self._openai_quest(
            self.relevant_components_prompt_template, template_variables
        )
        relevant_components = llm_ans.split(", ")
        return relevant_components

    def _openai_quest_workflow(self, task: str):
        template_variables = self._template_variables_workflow_prompt(task)
        llm_ans = self._openai_quest(self.workflow_prompt_template, template_variables)
        return llm_ans

    def _openai_quest_workflow_modification(self, instruction: str):
        template_variables = self._template_variables_workflow_modification_prompt(
            instruction
        )
        llm_ans = self._openai_quest(
            self.workflow_modification_prompt_template, template_variables
        )
        return llm_ans

    def _openai_quest_component(self, description: str, input_labels: List):
        template_variables = self._template_variables_component_prompt(
            description, input_labels
        )
        llm_ans = self._openai_quest(self.component_prompt_template, template_variables)
        return llm_ans

    def _template_variable_label_suffix(
        self, input_label: str, template_variable_label: str
    ):
        label_suffix = template_variable_label.replace(
            TEMPLATE_VARIABLE_KEY_PREFIX.format(label=input_label), ""
        )
        return label_suffix

    def _add_dependencies_llm_repr(
        self, workflow_llm_repr: Dict, workflow: WorkflowModel
    ):
        for dependency in workflow.dependencies:
            input_label = dependency.component_input_key
            source_label = dependency.source_label
            source_value = COMPONENT_SOURCE_REPR.format(label=source_label)
            target_label = dependency.target_label
            template_variable_label = dependency.template_variable_key
            try:
                input_label_dict = workflow_llm_repr[target_label]["input_labels"][
                    input_label
                ]
            except KeyError:
                warnings.warn(
                    f"Could not find input label '{input_label}' "
                    f"of component {target_label}. Skipping!"
                )
                continue
            if template_variable_label:
                template_variable_label = self._template_variable_label_suffix(
                    input_label, template_variable_label
                )
                input_label_dict["template_variables"][
                    template_variable_label
                ] = source_value
            else:
                input_label_dict["value"] = source_value

    def _template_variables_llm_repr_hardcoded(
        self, input_label: str, template_variables: Dict
    ):
        template_variable_llm_repr = {}
        for label, value in template_variables.items():
            new_label = self._template_variable_label_suffix(input_label, label)
            template_variable_llm_repr[new_label] = value
        return template_variable_llm_repr

    def component_input_value_llm_repr_hardcoded(self, component_input: ComponentInput):
        if isinstance(component_input.value, File):
            return component_input.value.path
        if (
            isinstance(component_input.value, list)
            or isinstance(component_input.value, dict)
            or isinstance(component_input.value, int)
        ):
            return component_input.value
        return str(component_input.value)

    def _input_labels_llm_repr_hardcoded(
        self, component_inputs: Union[List[ComponentInput], ComponentInput]
    ):
        input_labels_llm_repr = {}
        if isinstance(component_inputs, ComponentInput):
            component_inputs = [component_inputs]
        for component_input in component_inputs:
            input_label = component_input.key
            template_variables_repr = self._template_variables_llm_repr_hardcoded(
                input_label,
                component_input.template_variables,
            )
            input_labels_llm_repr[input_label] = {
                "value": self.component_input_value_llm_repr_hardcoded(component_input),
                "template_variables": template_variables_repr,
            }  # Values intended to be overwritten by source component labels if connected
        return input_labels_llm_repr

    def _component_llm_repr(
        self, component: ComponentModel, registry_description: bool = True
    ):
        description = component.description
        if registry_description:
            description = (
                self._component_description(component.class_name) or description
            )
        component_llm_repr = {
            "name": component.name if component.is_custom else component.class_name,
            "description": description,
            "input_labels": self._input_labels_llm_repr_hardcoded(component.inputs),
        }
        return component_llm_repr

    def _workflow_llm_repr(self, workflow: WorkflowModel = None):
        workflow = workflow or self.workflow
        components_ordered = workflow.components_ordered()
        workflow_llm_repr = {}
        for component in components_ordered:
            component_llm_repr = self._component_llm_repr(component)
            workflow_llm_repr[component.label] = component_llm_repr
        self._add_dependencies_llm_repr(workflow_llm_repr, workflow)
        return workflow_llm_repr

    def _workflow_llm_repr_str(
        self, workflow: WorkflowModel = None, indent: int = None
    ):
        workflow_llm_repr = self._workflow_llm_repr(workflow)
        workflow_llm_repr_str = json.dumps(workflow_llm_repr, indent=indent)
        return workflow_llm_repr_str

    def _llm_repr_str2workflow(self, llm_ans: str, workflow: WorkflowModel = None):
        workflow = workflow or self.workflow
        llm_repr = self._llm_str2json(llm_ans)
        llm_repr = self._postprocess_llm_repr(llm_repr)
        logger.debug(
            f"Post-processed LLM representation to:\n{json.dumps(llm_repr, indent=4)}\n"
        )
        id2component = {  # TODO: don't create new custom components when modifying workflow? (or allow changing?)
            id: self._create_component_by_classname(
                id_data["name"], id_data["description"], id_data["input_labels"], id
            )
            for id, id_data in llm_repr.items()
        }
        dependencies = self._add_component_inputs(llm_repr, id2component)
        workflow.components = list(id2component.values())
        workflow.dependencies = dependencies
        workflow.auto_component_position()
        logger.debug(f"Created the following workflow:\n{self.workflow}\n")
        return workflow

    def _create_empty_modification_workflow(self):
        empty_workflow = self.workflow.model_copy(deep=True)
        empty_workflow.dependencies = []
        empty_workflow.components = []
        empty_workflow.description = (
            self.workflow.description
        )  # TODO: update description after modification (probably not here though)
        empty_workflow.version = (
            self.workflow.version
        )  # TODO: new version for new workflow?
        return empty_workflow

    def _add_property_getter(
        self, llm_repr: Dict[str, Dict[str, Any]], component_label: str, field: str
    ):
        property_getter_label = f"{COMPONENT_LABEL_PREFIX}{len(llm_repr) + 1}"
        if property_getter_label in llm_repr:
            warnings.warn(
                "Error when post-processing LLM answer. Component label {property_getter_label} already used. Overwriting!"
            )
        llm_repr[property_getter_label] = {
            "name": "PropertyGetter",
            "input_labels": {
                "Input": {"value": COMPONENT_SOURCE_REPR.format(label=component_label)},
                "Selected property": {"value": field},
            },
            "description": self._component_description("PropertyGetter"),
        }
        return property_getter_label

    def _postprocess_missed_property_getters(
        self, llm_repr: Dict[str, Dict[str, Any]]
    ):  # For errors like [COMPONENT2.preview] (both in input_values and template variable values)
        for component_data in list(
            llm_repr.values()
        ):  # list: to copy, since new values might be added
            for input_label_data in component_data["input_labels"].values():
                input_value = input_label_data["value"]
                if isinstance(input_value, str):
                    matches = regex.findall(MISSED_PROPERTY_GETTER_PATTERN, input_value)
                    for full_match, component_label, field in matches:
                        property_getter_label = self._add_property_getter(
                            llm_repr, component_label, field
                        )
                        input_value = input_value.replace(
                            full_match,
                            COMPONENT_SOURCE_REPR.format(label=property_getter_label),
                        )
                    input_label_data["value"] = input_value
                for template_variable, template_variable_value in input_label_data.get(
                    "template_variables", dict()
                ).items():
                    if isinstance(template_variable, str):
                        matches = regex.findall(
                            MISSED_PROPERTY_GETTER_PATTERN, template_variable_value
                        )
                        for full_match, component_label, field in matches:
                            property_getter_label = self._add_property_getter(
                                llm_repr, component_label, field
                            )
                            template_variable_value = template_variable_value.replace(
                                full_match,
                                COMPONENT_SOURCE_REPR.format(label=property_getter_label),
                            )
                        input_label_data["template_variables"][
                            template_variable
                        ] = template_variable_value
        return llm_repr

    def _postprocess_missed_template_variables(
        self, llm_repr: Dict[str, Dict[str, Any]]
    ):  # For errors like "This is a text with a template variable [COMPONENT1]"
        component_reprs = {
            id: COMPONENT_SOURCE_REPR.format(label=id) for id in llm_repr
        }
        for component_data in llm_repr.values():
            for input_label_data in component_data["input_labels"].values():
                input_value = input_label_data["value"]
                if isinstance(input_value, str):
                    for id, component_repr in component_reprs.items():
                        if (
                            component_repr in input_value
                            and input_value != component_repr
                        ):
                            template_variable = id.lower()
                            template_variable_repr = TEMPLATE_VARIABLE_REPR.format(
                                template_variable=template_variable
                            )
                            input_value = input_value.replace(
                                component_repr, template_variable_repr
                            )
                            input_label_data["template_variables"][
                                template_variable
                            ] = component_repr
                    input_label_data["value"] = input_value
        return llm_repr

    def _postprocess_misformatted_template_variables(
        self, llm_repr: Dict[str, Dict[str, Any]]
    ):  # For errors like "This is a text with a template variable input_str" where 'input_str' is still defined among template variables
        for component_data in llm_repr.values():
            for input_label_data in component_data["input_labels"].values():
                if "template_variables" in input_label_data:
                    input_value = input_label_data["value"]
                    if isinstance(input_value, str):
                        for template_variable in input_label_data["template_variables"]:
                            template_variable_repr = TEMPLATE_VARIABLE_REPR.format(
                                template_variable=template_variable
                            )
                            if template_variable_repr not in input_value:
                                input_value = input_value.replace(
                                    template_variable, template_variable_repr
                                )
                        input_label_data["value"] = input_value
        return llm_repr

    def _postprocess_llm_repr(self, llm_repr: Dict[str, Dict[str, Any]]):
        llm_repr = self._postprocess_misformatted_template_variables(llm_repr)
        llm_repr = self._postprocess_missed_property_getters(llm_repr)
        llm_repr = self._postprocess_missed_template_variables(llm_repr)
        return llm_repr

    def generate_custom_component(
        self,
        name: str = "PlaceHolder",
        description: str = "Returns the boolean True",
        input_labels: List[str] = None,
    ):
        input_labels = input_labels or []
        logger.debug(
            f"Asking LLM for a generation of a component with the following "
            f"description: \n{description}\nInput labels: {input_labels}\n"
        )
        component_code = self._openai_quest_component(description, input_labels)
        logger.debug(
            f"Got the following component code LLM answer:\n{component_code}\n"
        )
        component_code = self._postprocess_custom_component_code(component_code)
        logger.debug(
            f"Post-processed component code LLM answer to the following:\n{component_code}\n"
        )
        cm = ComponentModel(
            name=name,
            class_name="Custom",
            description=description,
            group="CUSTOM",
            inputs=[ComponentInput(key=key, data_type="ANY") for key in input_labels],
            output=ComponentOutput(data_type="ANY"),
            label=None,
            is_custom=True,
            component_code=r"{}".format(component_code),
        )
        return cm

    def generate_workflow_modification(self, modification_description: str):
        logger.debug(
            f"Asking LLM for a modification of the workflow according to the following "
            f"instruction:\n{modification_description}\n"
        )
        llm_ans = self._openai_quest_workflow_modification(modification_description)
        logger.debug(
            f"Got the following workflow modification LLM answer:\n{json.dumps(self._llm_str2json(llm_ans), indent=4)}\n"
        )
        empty_modification_workflow = self._create_empty_modification_workflow()
        modified_workflow = self._llm_repr_str2workflow(
            llm_ans, empty_modification_workflow
        )
        self.workflow = modified_workflow
        return modified_workflow

    def generate_workflow(self, files: List[File] = None):
        # files = [File(path='/remote/idiap.svm/home.active/sljungbeck/Confidential/lunar/lunarcore/tests/auto_workflow/tests/file_content_searcher/files/my_text_file.txt', description='The text file to search in')]
        # self.workflow.description = "Create a workflow that reads a file and outputs 'Yes' if it contains the string 'abc', and outputs 'No' otherwise."
        self._add_files(files or [])
        logger.debug(
            f"Asking LLM for a generation of a workflow with the following "
            f"description:\n{self.workflow.description}\n"
        )
        llm_ans = self._openai_quest_workflow(self.workflow.description)
        # llm_ans = '{"COMPONENT1": {"name": "UploadComponent", "description": "Uploads local files to the server.\\n    Input (str): A string of the local path of the local file to upload to the server. If needed, tha local path can be inputted manually by the user.\\n    Output (str): A string of the server path of the uploaded file.", "input_labels": {"Input file": {"value": "/remote/idiap.svm/temp.rea01/sljungbeck/lunar/lunarcore/lunarcore/tests/auto_workflow/tests/file_integers_adder/files/integers.txt", "template_variables": {}}}}, "COMPONENT2": {"name": "FileReader", "description": "Takes a server path of a file as input and reads it. Outputs the content as a string.    \\nInput (str): The server path of the file to read.    \\nOutput (str): The content of the file.", "input_labels": {"File path": {"value": "[COMPONENT1]"}}}, "COMPONENT3": {"name": "PythonCoder", "description": "Performs customized Python code execution. Outputs the value that the Python variable `result` is set to during the execution of the Python code.\\nInputs:\\n  `Code` (str): A string of the Python code to execute.  If needed, the Python code can be inputted manually by the user.\\nOutput (Any): The value of the variable `result` in the Python code after execution.", "input_labels": {"Code": {"value": "integers_str = \\"\\"\\"{input_str}\\"\\"\\"\\nintegers_list = map(int, integers_str.split(\',\'))\\nresult = sum(integers_list)", "template_variables": {"input_str": "[COMPONENT2]"}}}}}'
        # llm_ans = '{"COMPONENT1": {"name": "YahooFinanceAPI", "description": "Connects to Yahoo\'s public API and retrieves financial data about companies and their stocks.\\n    Input (List[str]): A list of strings of the tickers to the stocks to get data about.\\n    Output (Dict[str,Dict[str, Any]]): A dictionary mapping each inputted ticker (str) to the financial data about the corresponding stock in the form of a dictionary of indicators (str) mapped to their values (Any)", "input_labels": {"Tickers": {"value": ["MMM"], "template_variables": {}}}}, "COMPONENT2": {"name": "PropertyGetter", "description": "Extracts the mapped value of an inputted key/field/attribute in an inputted object/datastructure. It can be the value of a field/attribute in an object, or the mapped value of a key in a dictionary.\\nInputs:\\n  `Input` (Any): An object to extract a value from. The object can for example be a dictionary, a list, or a File object.\\n  `Selected property` (str): A string of the name of the key/field/attribute to extract from the inputted object. If needed, the key/field/attribute can be inputted manually by the user. If nested objects/dicts, nested keys can be accessed by concatenating keys with dots (e.g. `parent_dict_key.dict_key`). If, for example, a list of dicts (List[Dict]) is inputted, the list indices are used as keys (e.g. `list_index.dict_key`).\\nOutput (Any): The mapped value of the inputted key/field/attribute in the inputted object.", "input_labels": {"Input": {"value": "[COMPONENT1]", "template_variables": {}}, "Selected property": {"value": "MMM.earnings", "template_variables": {}}}}}'
        # logger.debug(f'Got the following workflow LLM answer:\n{json.dumps(self._llm_str2json(llm_ans), indent=None)}\n')
        logger.debug(
            f"Got the following workflow LLM answer:\n{json.dumps(self._llm_str2json(llm_ans), indent=4)}\n"
        )
        self.workflow = self._llm_repr_str2workflow(llm_ans)

        # TODO: remove
        # self.generate_workflow_modification('Add a report in the end of the workflow.')

        return self.workflow


if __name__ == "__main__":
    workflow = WorkflowModel(name="untitled", description="generate a workflow that creates a report")
    auto_workflow = AutoWorkflow(workflow=workflow)
    generated_workflow = auto_workflow.generate_workflow()
    print(generated_workflow)

