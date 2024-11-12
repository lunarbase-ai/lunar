# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import ast
import hashlib
import json
import os.path
import re
import zipfile
from functools import cached_property
from json import JSONDecodeError
from time import time
from typing import Any, ClassVar, Dict, List, Optional, Union
from uuid import uuid4

import networkx as nx
import requirements
from autoimport import fix_code
from jinja2 import Template
from lunarcore.component.lunar_component import (
    LunarComponent,
    COMPONENT_DESCRIPTION_TEMPLATE,
)

from lunarbase.config import GLOBAL_CONFIG
from lunarbase.modeling.component_encoder import ComponentEncoder
from lunarbase.utils import (
    isiterable,
    to_camel,
    to_jinja_template,
    get_imports,
    anyinzip,
    anyindir,
)
from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.data_types import DataType, File
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_serializer,
    field_validator,
    model_validator,
    computed_field,
)
from pydantic_core.core_schema import ValidationInfo
from requirements.requirement import Requirement

UNDEFINED = ":undef:"
REQ_FILE_NAME = "requirements.txt"
PYTHON_CODER_NAME = "PythonCoder"


class ComponentInput(BaseModel):
    key: str = Field(...)
    data_type: Union[DataType, str] = Field(...)
    value: Optional[Any] = Field(default=UNDEFINED)
    template_variables: Dict[str, Any] = Field(default_factory=dict)
    component_id: Optional[str] = Field(default=None)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            DataType: lambda out_type: str(out_type.name),
        }
        validate_assignment = True

    @field_validator("data_type")
    @classmethod
    def validate_types(cls, value):
        if isinstance(value, str):
            try:
                value = DataType[value.upper()]
            except KeyError:
                value = DataType(value)
        return value

    @field_serializer("data_type", when_used="always")
    def serialize_data_type(value):
        if isinstance(value, DataType):
            return value.value
        return value

    @field_validator("value")
    @classmethod
    def validate_value(cls, value, info: ValidationInfo):
        data_type = info.data.get("data_type")

        if data_type == DataType.ANY:
            return value

        if data_type in [DataType.LIST, DataType.STREAM] and value == UNDEFINED:
            return []

        if data_type == DataType.STREAM and isiterable(value):
            return value

        if isinstance(value, data_type.type()) or (
            isinstance(value, list)
            and len(value) > 0
            and isinstance(value[0], data_type.type())
        ):
            return value

        if (
            value == UNDEFINED
            or value is None
            or (data_type is not None and data_type.type() is any)
        ):
            return value

        if data_type is None:
            raise ValueError("Something went wrong, <data_type> not found.")

        # TODO: For backward compatibility - to be reviewed
        if isinstance(value, str) and data_type == DataType.FILE:
            value = File(path=value, name=os.path.split(value)[-1])
            return value

        if isinstance(value, str) and data_type == DataType.INT:
            try:
                value = int(value)
                return value
            except ValueError:
                raise ValueError(
                    f"Expected value {value} to have type {data_type} (real type: {data_type.type()}) but got {type(value)}!"
                )

        if isinstance(value, str) and data_type == DataType.FLOAT:
            try:
                value = float(value)
                return value
            except ValueError:
                raise ValueError(
                    f"Expected value {value} to have type {data_type} (real type: {data_type.type()}) but got {type(value)}!"
                )

        # This may break some use cases, although it shouldn't
        if data_type in [DataType.LIST, DataType.STREAM] and not isiterable(value):
            value = [value]
            return value

        if issubclass(data_type.type(), BaseModel):
            value = data_type.type().model_validate(value)
            return value

        if data_type == DataType.JSON and isinstance(value, File):
            value = value.dict()
            return value

        if data_type == DataType.JSON and isinstance(value, str):
            try:
                value = json.loads(value)
                return value
            except JSONDecodeError as e:
                raise ValueError(
                    f"Expected value {value} to have type {data_type} (real type: {data_type.type()}) "
                    f"but got {type(value)} and casting failed with {str(e)}!"
                )

        if data_type == DataType.AGGREGATED:
            return {}

        raise ValueError(
            f"Expected value {value} to have type {data_type} (real type: {data_type.type()}) but got {type(value)}!"
        )

    @field_validator("template_variables")
    @classmethod
    def validate_templated_variables(cls, value, info: ValidationInfo):
        input_value = info.data.get("value", UNDEFINED)
        if (
            info.data.get("data_type", None)
            not in [
                DataType.TEMPLATE,
                DataType.CODE,
                DataType.R_CODE,
                DataType.GRAPHQL,
                DataType.SQL,
                DataType.SPARQL,
            ]
            or len(value) == 0
            or input_value == UNDEFINED
            or len(input_value) == 0
        ):
            return value

        if info.data.get("data_type", None) is DataType.CODE:
            return {
                tmpl_var_key: str(
                    tmpl_var_value.model_dump()
                    if isinstance(tmpl_var_value, BaseModel)
                    else tmpl_var_value
                )
                for tmpl_var_key, tmpl_var_value in value.items()
            }

        try:
            root_var = list(
                {tmpl_var_key.split(".")[0] for tmpl_var_key, _ in value.items()}
            )
            if len(root_var) != 1 or root_var[0] != info.data.get("key", ""):
                raise ValueError(
                    f"Ambiguous template variable grouping: got {root_var} as parent variables, expected {info.data.get('key', [])}!"
                )
            _ = {
                tmpl_var_key.split(".")[1]: tmpl_var_val
                for tmpl_var_key, tmpl_var_val in value.items()
            }
        except IndexError:
            raise ValueError(
                f"Expected canonical template variable names (e.g., <input_variable.template_variable>). Got {list(value.keys())}"
            )
        return value

    def __hash__(self):
        value_for_hashing = str(self.value)
        if value_for_hashing == UNDEFINED:
            value_for_hashing = str(uuid4())
        tmp_var_values = ".".join(
            [
                f"{tmp_var_key}:{tmp_var_value}"
                for tmp_var_key, tmp_var_value in self.template_variables.items()
            ]
        )
        hash_object = hashlib.md5(
            f"{self.key}{str(self.data_type)}{value_for_hashing}{tmp_var_values}".encode()
        )
        return int(hash_object.hexdigest(), 16)

    def __eq__(self, other):
        if not isinstance(other, ComponentInput):
            raise NotImplementedError()

        this_value_for_eq = self.value
        if this_value_for_eq == UNDEFINED:
            this_value_for_eq = str(uuid4())

        return (
            self.key == other.key
            and self.data_type == other.data_type
            and this_value_for_eq == other.value
        )

    def resolve_template_variables(self):
        if (
            self.data_type not in [DataType.TEMPLATE, DataType.CODE]
            or len(self.template_variables) == 0
        ):
            return self.value

        split_tmpl_vars = dict()
        for tmpl_var_key, tmpl_var_val in self.template_variables.items():
            parent, _, var = tmpl_var_key.partition(".")
            split_tmpl_vars[var if len(var) > 0 else parent] = tmpl_var_val
        jinja_template = to_jinja_template(str(self.value), list(split_tmpl_vars))
        return Template(jinja_template).render(split_tmpl_vars)


class ComponentOutput(BaseModel):
    data_type: Union[DataType, str] = Field(...)
    value: Optional[Any] = Field(default=UNDEFINED)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            DataType: lambda out_type: str(out_type.name),
        }
        validate_assignment = True

    @field_validator("data_type")
    @classmethod
    def validate_types(cls, value):
        if isinstance(value, str):
            try:
                value = DataType[value.upper()]
            except KeyError:
                value = DataType(value)
        return value

    @field_serializer("data_type", when_used="always")
    def serialize_data_type(value):
        if isinstance(value, DataType):
            return value.value
        return value

    @field_serializer("value", when_used="json-unless-none")
    def serialize_value(self, value: Any):
        if value is None:
            return value
        json_value = json.dumps(value, cls=ComponentEncoder)
        # preserve the original data type
        return json.loads(json_value)

    @field_validator("value")
    @classmethod
    def validate_value(cls, value, info: ValidationInfo):
        if value is None:
            return value
        if isinstance(value, str) and value == UNDEFINED:
            return value
        dtype = info.data.get("data_type")
        if value == UNDEFINED or dtype.type() is any:
            return value
        if issubclass(dtype.type(), BaseModel):
            value = dtype.type().model_validate(value)

        if dtype == DataType.STREAM and value != UNDEFINED:
            return value

        if dtype is None:
            raise ValueError("Something went wrong, <data_type> not found.")
        if (
            isinstance(value, list)
            and len(value) > 0
            and isinstance(value[0], dtype.type())
        ):
            return value
        if not isinstance(value, dtype.type()):
            raise ValueError(
                f"Expected value {value} to have type {dtype} (real type: {dtype.type()}) but got {type(value)}!"
            )
        return value


class ComponentPosition(BaseModel):
    x: Union[int, float] = Field(default=0.0)
    y: Union[int, float] = Field(default=0.0)


class ComponentModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )  # Unique across all components
    workflow_id: Optional[str] = Field(
        default=None,
    )  # Ref to parent workflow - used for venv, file connector, etc.
    name: str = Field(...)
    class_name: str = Field(...)
    description: str = Field(...)
    group: Optional[Union[str, ComponentGroup]] = Field(
        default=ComponentGroup.UNCLASSIFIED
    )
    inputs: Union[List[ComponentInput], ComponentInput] = Field(...)
    output: ComponentOutput = Field(...)
    label: Optional[str] = Field(default=None)  # Unique within the workflow scope
    configuration: Dict = Field(default_factory=dict)
    version: Optional[str] = Field(default=None)
    is_custom: bool = Field(default=False)
    is_terminal: bool = Field(default=False)
    position: ComponentPosition = Field(default=ComponentPosition())
    timeout: int = Field(default=600)
    component_code: Optional[Union[Dict, str]] = Field(default=None)
    component_code_requirements: List[str] = Field(
        default_factory=list, validate_default=True
    )
    component_example_path: Optional[str] = Field(default=None)
    invalid_errors: List[str] = Field(default=[])

    validation_invalid_errors: ClassVar[List[str]] = []

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_attributes_allowed = True
        json_encoders = {
            DataType: lambda out_type: str(out_type.name),
            ComponentGroup: lambda group: str(group.name),
        }
        validate_assignment = True

    @field_validator("group")
    @classmethod
    def validate_group(cls, value):
        if isinstance(value, str):
            try:
                value = ComponentGroup[value.upper()]
            except KeyError:
                value = ComponentGroup.UNCLASSIFIED

        return value

    @field_serializer("group", when_used="always")
    def serialize_group(value):
        if isinstance(value, ComponentGroup):
            return value.value
        return value

    @field_validator("inputs", mode="before")
    @classmethod
    def validate_inputs(cls, value):
        if not isinstance(value, list):
            value = [value]

        validated_inputs = []
        for component_input in value:
            try:
                if isinstance(component_input, ComponentInput):
                    component_input = component_input.dict()
                component_input = ComponentInput.model_validate(component_input)
                validated_inputs.append(component_input)
            except ValidationError as validation_error:
                cls.validation_invalid_errors.append(repr(validation_error))
        return validated_inputs

    @field_validator("output", mode="before")
    @classmethod
    def validate_output(cls, value):
        try:
            if isinstance(value, ComponentOutput):
                value = value.dict()
            validated_output = ComponentOutput(**value)
            return validated_output
        except ValidationError as validation_error:
            cls.validation_invalid_errors.append(repr(validation_error))
            return ComponentOutput(data_type=DataType.ANY, value=None)

    @field_validator("invalid_errors")
    @classmethod
    def validate_invalid_errors(cls, value):
        cls.validation_invalid_errors.extend(value)
        errors = cls.validation_invalid_errors
        cls.validation_invalid_errors = []
        return errors

    @field_validator("label")
    @classmethod
    def validate_label(cls, value, info: ValidationInfo):
        if value is None:
            value = f"{info.data.get('class_name', '')}_{info.data.get('id', '')}"
        return value

    @field_serializer("component_code", when_used="always")
    def serialize_component_code(value):
        if value is None:
            return None

        if os.path.isfile(str(value)):
            return os.path.relpath(str(value), GLOBAL_CONFIG.COMPONENT_LIBRARY_PATH)
        return value

    @field_validator("component_code")
    @classmethod
    def validate_component_code(cls, value):
        # Dependencies will not be fixed for explicitly defined classes.
        if value is None:
            return value

        if not os.path.isabs(value):
            value = os.path.join(GLOBAL_CONFIG.COMPONENT_LIBRARY_PATH, value)

        if not os.path.isfile(str(value)):
            raise ValueError(f"Failed to locate source code for component at {value}")
        return value

    @field_validator("component_code_requirements")
    @classmethod
    def validate_component_code_requirements(cls, value, info: ValidationInfo):
        """
        This does not look into the component code. Code requirements are checked at registering time.
        """

        _component_code = info.data.get("component_code")
        if _component_code is None:
            return value

        reqs = []
        if info.data.get("class_name", "") == PYTHON_CODER_NAME:
            for _inp in info.data.get("inputs", []):
                if (
                    _inp.data_type == DataType.CODE
                    and _inp.value is not None
                    and _inp.value != UNDEFINED
                ):
                    source_code_text = f"\n{_inp.value}"
                    try:
                        reqs.extend(
                            [
                                Requirement(imp)
                                for imp in get_imports(source_code=source_code_text)
                            ]
                        )
                    except Exception as e:
                        raise ValueError(
                            f"Failed to parse requirements for PythonCoder component. "
                            f"This component may not work. Please please check the import section {str(e)}"
                        )
                    return list({r.line or r.name for r in reqs})

        for spec in value:
            try:
                spec = Requirement(spec)
                reqs.append(spec)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse requirements for component {info.data['name']}. "
                    f"This component may not work. Please follow common requirements.txt rules! Details: {str(e)}"
                )

        if zipfile.is_zipfile(_component_code):
            with zipfile.ZipFile(_component_code) as z:
                try:
                    req_text = str(z.read(REQ_FILE_NAME))
                    reqs.extend([req for req in requirements.parse(req_text)])

                except KeyError:
                    pass
                except Exception as e:
                    raise ValueError(
                        f"Failed to parse requirements for component {info.data['name']}. "
                        f"This component may not work. Please follow common requirements.txt rules! Details: {str(e)}"
                    )
        else:
            req_file_path = os.path.abspath(os.path.dirname(_component_code))
            req_file_path = os.path.join(req_file_path, REQ_FILE_NAME)
            if os.path.isfile(req_file_path):
                with open(req_file_path, "r") as fd:
                    try:
                        reqs.extend([req for req in requirements.parse(fd)])
                    except Exception as e:
                        raise ValueError(
                            f"Failed to parse requirements for component {info.data['name']}. "
                            f"This component may not work. Please follow common requirements.txt rules! Details: {str(e)}"
                        )

        # return [r.name or r.line for r in reqs if importlib.util.find_spec(r.name or r.line or "") is None]
        return list({r.line or r.name for r in reqs})

    @field_serializer("component_example_path", when_used="always")
    def serialize_component_example_path(value):
        if value is None:
            return value

        if os.path.isfile(str(value)):
            return os.path.relpath(str(value), GLOBAL_CONFIG.COMPONENT_LIBRARY_PATH)
        return value

    @field_validator("component_example_path")
    @classmethod
    def validate_component_example_path(cls, value):
        if value is None:
            return value

        if not os.path.isabs(value):
            value = os.path.join(GLOBAL_CONFIG.COMPONENT_LIBRARY_PATH, value)
        if not os.path.isfile(value):
            value = None
        return value

    @model_validator(mode="after")
    def validate_component(self):
        if self.component_example_path is not None:
            return self

        if self.component_code is not None:
            _example = os.path.join(
                os.path.dirname(self.component_code),
                GLOBAL_CONFIG.COMPONENT_EXAMPLE_WORKFLOW_NAME,
            )
            if os.path.isfile(_example):
                self.component_example_path = _example
        return self

    def get_input(self, input_key: str):
        for inp in self.inputs:
            if inp.key == input_key:
                return inp
        raise KeyError(f"Input {input_key} not found in component {self.label}")

    def get_component_example(self):
        if self.component_example_path is None:
            return None

        if not os.path.isfile(self.component_example_path):
            return None
        try:
            with open(self.component_example_path, "r") as f:
                wf = json.load(f)
            return WorkflowModel.parse_obj(wf)
        except json.JSONDecodeError:
            return None

    # def get_callables(self):
    #     _component_code = self.component_code
    #
    #     if _component_code is None:
    #         return dict()
    #
    #     code = compile(_component_code, "/dev/null", "exec")
    #     inner_vars = {}
    #     exec(code, inner_vars)
    #     return {
    #         attr: attr_val
    #         for attr, attr_val in inner_vars.items()
    #         if attr != "__builtins__"
    #     }


class ComponentDependency(BaseModel):
    component_input_key: str = Field(default=...)
    source_label: str = Field(default=...)
    target_label: str = Field(default=...)
    template_variable_key: Optional[str] = Field(default=None)

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True

    @model_validator(mode="after")
    def validate_dependency(self):
        src = self.source_label or "dummy_source"
        tgt = self.target_label or "dummy_source"

        assert (
            src != tgt
        ), f"Self dependency are not supported but encountered in {src}!"

        return self


class AutoComponentSpacing(BaseModel):
    dx: Union[int, float] = Field(default=450.0)
    dy: Union[int, float] = Field(default=350.0)
    x0: Union[int, float] = Field(default=0.0)
    y0: Union[int, float] = Field(default=0.0)


class WorkflowRuntimeModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str = Field(default=...)
    state: str = Field(default=...)
    elapsed: float = Field(default=0.0)
    name: Optional[str] = Field(default=None)


class WorkflowModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default=...)
    description: str = Field(default=...)
    version: Optional[str] = Field(default=None)
    components: List[ComponentModel] = Field(default_factory=list)
    dependencies: List[ComponentDependency] = Field(default_factory=list)
    timeout: int = Field(default=3600)
    auto_component_spacing: Optional[AutoComponentSpacing] = Field(
        default=AutoComponentSpacing()
    )
    invalid_errors: List[str] = Field(default=[])

    validation_invalid_errors: ClassVar[List[str]] = []

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        validate_assignment = True
        arbitrary_attributes_allowed = True
        json_encoders = {
            DataType: lambda out_type: str(out_type.name),
            ComponentGroup: lambda group: str(group.name),
        }

    def short_model(self):
        return WorkflowModel(
            id=self.id,
            name=self.name,
            description=self.description,
            invalid_errors=self.invalid_errors,
        )

    def get_dag(self):
        dag = nx.MultiDiGraph()
        dag.add_nodes_from([comp.label for comp in self.components])
        edges = [
            (
                dep.source_label,
                dep.target_label,
                {"data": (dep.component_input_key, dep.template_variable_key)},
            )
            for dep in self.dependencies
        ]

        dag.add_edges_from(edges)
        return dag

    def label2component(self):
        label2component = {component.label: component for component in self.components}
        return label2component

    def components_ordered(self):
        components_ordered = []
        for layer in self.bfs_layers_components():
            components_ordered += layer
        return components_ordered

    def bfs_layers_components(self):
        label2component = self.label2component()
        bfs_layers_labels = self.bfs_layers_labels()
        bfs_layers_components = []
        for layer_labels in bfs_layers_labels:
            layer_components = [label2component[label] for label in layer_labels]
            bfs_layers_components.append(layer_components)
        return bfs_layers_components

    def bfs_layers_labels(self):
        dag = self.get_dag()
        roots = [node for node in dag.nodes() if dag.in_degree(node) == 0]
        layers = [roots]
        seen = set(roots)
        while len(seen) < dag.number_of_nodes():
            layers.append([])
            for node in layers[-2]:
                for nb in dag.neighbors(node):
                    if nb not in seen:
                        layers[-1].append(nb)
                        seen.add(nb)
        return layers

    def auto_component_position(
        self,
    ):  # TODO: fix so that arrows cannot go to left (fix so components are as late as possible instead of as early as possible) (Topsort?)
        label2component = self.label2component()
        xnow = self.auto_component_spacing.x0
        for layer in self.bfs_layers_labels():
            ynow = self.auto_component_spacing.y0
            for component_label in layer:
                label2component[component_label].position = ComponentPosition(
                    x=xnow, y=ynow
                )
                ynow += self.auto_component_spacing.dy
            xnow += self.auto_component_spacing.dx

    @field_validator("components", mode="before")
    @classmethod
    def validate_components(cls, value, info: ValidationInfo):
        if not isinstance(value, list):
            cls.validation_invalid_errors.append(
                "The 'components' property must be a list of component models"
            )
            return []

        validated_components = []
        invalid_components_count = 0
        for component_model in value:
            if isinstance(component_model, ComponentModel):
                component_model = component_model.dict()

            try:
                component_model = ComponentModel.model_validate(component_model)
                cls.validation_invalid_errors.extend(component_model.invalid_errors)
                validated_components.append(component_model)
            except ValidationError as validation_error:
                # Tries to recover component information from the dictionary
                name = (
                    component_model["name"]
                    if "name" in component_model
                    else "Invalid component"
                )
                description = (
                    component_model["description"]
                    if "description" in component_model
                    else "An error occurred while loading this component."
                )
                label = (
                    component_model["label"]
                    if "label" in component_model
                    else f"ERROR-{invalid_components_count}"
                )
                position = (
                    component_model["position"]
                    if "position" in component_model
                    else ComponentPosition()
                )
                error_component = ComponentModel(
                    name=name,
                    workflow_id=info.data.get("id", ""),
                    class_name="Error",
                    description=description,
                    label=label,
                    inputs=[],
                    output=ComponentOutput(
                        data_type=DataType.ANY,
                    ),
                    position=position,
                    invalid_errors=[repr(validation_error)],
                )
                validated_components.append(error_component)
                invalid_components_count += 1
                cls.validation_invalid_errors.append(repr(validation_error))
        return validated_components

    @field_validator("dependencies", mode="before")
    @classmethod
    def validate_dependencies(cls, value, info: ValidationInfo):
        if not isinstance(value, list):
            cls.validation_invalid_errors.append(
                "the 'dependencies' property must be a list of component models"
            )
            return []

        validated_dependencies = []
        # component_dict = {comp.label: comp for comp in info.data.get("components", [])}
        for dependency in value:
            try:
                if isinstance(dependency, ComponentDependency):
                    dependency = dependency.dict()
                validated_dependencies.append(ComponentDependency(**dependency))
            except ValidationError as validation_error:
                cls.validation_invalid_errors.append(repr(validation_error))
        return validated_dependencies

    @field_validator("invalid_errors")
    @classmethod
    def validate_invalid_errors(cls, value):
        cls.validation_invalid_errors.extend(value)
        errors = cls.validation_invalid_errors
        cls.validation_invalid_errors = []
        return errors

    @model_validator(mode="after")
    def validate_workflow(self):
        # Edges
        component_labels = {comp.label for comp in self.components}
        for dep in self.dependencies:
            if (
                dep.source_label not in component_labels
                or dep.target_label not in component_labels
            ):
                self.invalid_errors.append(
                    f"Either the source or the target of dependency {dep} not found in the components!"
                )

        dag = nx.MultiDiGraph()
        dag.add_nodes_from(list(component_labels))
        dag.add_edges_from(
            [
                (
                    dep.source_label,
                    dep.target_label,
                    {"data": (dep.component_input_key, dep.template_variable_key)},
                )
                for dep in self.dependencies
            ]
        )
        if not nx.is_directed_acyclic_graph(dag):
            self.invalid_error.append(f"Cycles encountered in workflow {self.name}!")

        terminals = {node for node in dag.nodes() if dag.out_degree(node) == 0}
        for i, comp in enumerate(self.components):
            if comp.label in terminals:
                self.components[i].is_terminal = True
            else:
                self.components[i].is_terminal = False

        return self


class WorkflowRuntime(BaseModel):
    """
    TODO: Not used yet but potentially useful for tracking workflow runtime and cancelling
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str = Field(default=...)
    pid: Optional[int] = Field(default=None)
    # If workflow exists here its state is RUNNING so no need for an explicit variable
    # state: str = Field(default=...)
    started: float = Field(default_factory=time)
    name: Optional[str] = Field(default=None)

    @property
    def elapsed(self):
        return time() - self.started


class RegisteredComponentModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_attributes_allowed = True
        validate_assignment = True

    EXPECTED_CLASS_VAR_TEMPLATES: ClassVar[List["Template"]] = [
        Template("{{ module_name }}/src/{{ module_name }}/__init__.py"),
        Template("src/{{ module_name }}/__init__.py"),
    ]
    package_path: str = Field(default=...)
    module_name: str = Field(default=...)

    @property
    def is_zip_package(self):
        return zipfile.is_zipfile(self.package_path)

    @field_validator("package_path")
    @classmethod
    def validate_package_path(cls, value):
        if not os.path.isfile(value) or os.path.isdir(value):
            raise ValueError(f"No such file or directory: {value}!")
        return value

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value, info: ValidationInfo):
        _package_path = info.data.get("package_path")
        class_path_candidates = [
            tmpl.render(module_name=value) for tmpl in cls.EXPECTED_CLASS_VAR_TEMPLATES
        ]
        if zipfile.is_zipfile(_package_path):
            class_path = anyinzip(_package_path, class_path_candidates)
            if not class_path:
                raise ValueError(
                    f"Package {_package_path} seems to be a zip file but none of paths {class_path_candidates} exist."
                )
        else:
            class_path = anyindir(_package_path, class_path_candidates)
            if not class_path:
                raise ValueError(
                    f"Package {_package_path} seems to be a directory but none of paths {class_path_candidates} exist."
                )

        return value

    @computed_field(return_type=ComponentModel)
    @cached_property
    def component_model(self):
        class_path_candidates = [
            tmpl.render(module_name=self.module_name)
            for tmpl in self.__class__.EXPECTED_CLASS_VAR_TEMPLATES
        ]
        if self.is_zip_package:
            class_path = anyinzip(self.package_path, class_path_candidates)
            with zipfile.ZipFile(self.package_path) as z:
                source_code = z.read(class_path).decode("utf-8")
        else:
            class_path = anyindir(self.package_path, class_path_candidates)
            with open(os.path.join(self.package_path, class_path), "r") as f:
                source_code = f.read()

        try:
            source_code = fix_code(source_code)
        except Exception as e:
            raise ValueError(str(e))

        tree = ast.parse(source_code)
        component_class_defs = [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        if len(component_class_defs) < 1:
            raise ValueError(
                f"A component definition must inherit from {LunarComponent.__name__}. "
                f"Code at {self.package_path} contains {len(component_class_defs)} classes!"
            )

        component_class, component_class_name = None, None
        base_class_names = set()
        for _cls in component_class_defs:
            base_class_names = {b.id for b in _cls.bases}
            if LunarComponent.__name__ in base_class_names:
                component_class = _cls
                component_class_name = _cls.name
                break

        if (
            component_class_name is None
            or LunarComponent.__name__ not in base_class_names
        ):
            raise ValueError(
                f"Main class in {self.class_path} must inherit {LunarComponent.__name__}!"
            )

        keywords = ",".join(
            [f'"{kw.arg}": {ast.unparse(kw.value)}' for kw in component_class.keywords]
        )

        keywords = re.sub(r"(?<!\w)\'|\'(?!\w)", '"', keywords)
        keywords = re.sub(r"DataType\.(\w+)", r'"\1"', keywords)
        keywords = re.sub(r"ComponentGroup\.(\w+)", r'"\1"', keywords)
        keywords = re.sub(r":\s?(None)", r':"\1"', keywords)
        keywords = json.loads("{" + keywords + "}")

        _component_description = keywords.pop("component_description", None)
        if _component_description is None or _component_description == "":
            _component_description = COMPONENT_DESCRIPTION_TEMPLATE

        # We ca assume all source imports ar captured in the requirements.txt
        """
        source_imports = []
        for imported in get_imports(source_code=source_code):
            try:
                imported = Requirement(imported)
                source_imports.append(imported)
            except ValueError as e:
                raise ValueError(
                    f"Detected source code requirement {imported} but failed to parse it. Details: {str(e)}! Component from {self.package_path} may not work as expected!"
                )
        """

        try:
            input_types = keywords.pop("input_types").items()

            component_model = ComponentModel(
                name=keywords.pop("component_name"),
                label=None,
                class_name=component_class_name,
                description=_component_description,
                group=keywords.pop("component_group"),
                inputs=[],
                output=ComponentOutput(data_type=keywords.pop("output_type")),
                component_code=self.package_path,
                component_code_requirements=[
                    f"{self.module_name} @ file://{self.package_path}"
                ],
                configuration={"force_run": False, **keywords},
            )
            inputs = [
                ComponentInput(
                    key=_in_name,
                    data_type=_in_type,
                    component_id=component_model.id,
                )
                for _in_name, _in_type in input_types
            ]
            component_model.inputs = inputs

        except KeyError as e:
            raise ValueError(
                f"Failed to parse component at {self.package_path}! "
                f"One or more expected attributes may be missing. Details: {str(e)}!"
            )

        return component_model
