# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import hashlib
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union
from uuid import uuid4

import networkx as nx
from jinja2 import Template
from requirements.requirement import Requirement

from lunarbase.modeling.component_encoder import ComponentEncoder
from lunarbase.utils import (
    isiterable,
    to_camel,
    to_jinja_template,
    get_imports,
)
from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.data_types import DataType
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo

UNDEFINED = ":undef:"
PYTHON_CODER_NAME = "PythonCoder"


class ComponentInput(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
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
    def validate_value(cls, value: Any, info: ValidationInfo):
        if isinstance(value, str) and value.lower() in ["none", "null"]:
            return None

        data_type = info.data.get("data_type")
        if data_type == DataType.ANY:
            return value

        if data_type in [DataType.FILE]:  # Continue with other datasource input types
            # Treat this as a datasource reference
            if isinstance(value, str):
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

        if data_type in [DataType.LIST, DataType.STREAM] and not isiterable(value):
            return [value]

        if issubclass(data_type.type(), BaseModel):
            value = data_type.type().model_validate(value)
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

        if data_type in [DataType.LIST] and isinstance(value, str):
            try:
                loaded_value = json.loads(value)
                if isiterable(loaded_value):
                    return loaded_value
            except:
                return [value]

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
        if isinstance(value, str) and value.lower() in ["none", "null"]:
            value = None

        if value is None:
            return value

        if isinstance(value, str) and value == UNDEFINED:
            return value
        dtype = info.data.get("data_type")
        if dtype.type() is type(None) and value is not None:
            raise ValueError(f"Not expecting any return value but got {value}!")

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
    label: Optional[str] = Field(
        default=None, validate_default=True
    )  # Unique within the workflow scope
    configuration: Dict = Field(default_factory=dict)
    version: Optional[str] = Field(default=None)
    is_custom: bool = Field(default=False)
    is_terminal: bool = Field(default=False)
    position: ComponentPosition = Field(default=ComponentPosition())
    timeout: int = Field(default=600)
    ##### the following 2 fields have been moved to registered component model but kept here as well for backward compatibility #####
    component_code: Optional[Union[Dict, str]] = Field(default=None)
    component_code_requirements: Optional[List[str]] = Field(default=None)
    ##################################################################################################################################
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
    def validate_inputs(cls, value, info: ValidationInfo):
        if not isinstance(value, list):
            value = [value]

        self_id = info.data.get("id", None)
        validated_inputs = []
        for component_input in value:
            try:
                if isinstance(component_input, ComponentInput):
                    component_input = component_input.dict()
                component_input = ComponentInput.model_validate(component_input)
                component_input.component_id = self_id
                validated_inputs.append(component_input)
            except ValidationError as validation_error:
                cls.validation_invalid_errors.append(repr(validation_error))
        return validated_inputs

    @field_validator("output", mode="before")
    @classmethod
    def validate_output(cls, value, info: ValidationInfo):
        self_id = info.data.get("id", None)
        try:
            if isinstance(value, ComponentOutput):
                value = value.dict()
            validated_output = ComponentOutput(**value)
            validated_output.component_id = self_id
            return validated_output
        except ValidationError as validation_error:
            cls.validation_invalid_errors.append(repr(validation_error))
            return ComponentOutput(
                data_type=DataType.ANY, value=None, component_id=self_id
            )

    @field_validator("invalid_errors")
    @classmethod
    def validate_invalid_errors(cls, value):
        cls.validation_invalid_errors.extend(value)
        errors = cls.validation_invalid_errors
        cls.validation_invalid_errors = []
        return errors


    @field_validator("configuration")
    @classmethod
    def validate_configuration(cls, value):
        for config_attr, config_value in (value or dict()).items():
            if isinstance(config_value, str) and config_value.lower() in [
                "none",
                "null",
            ]:
                value[config_attr] = None
        return value

    def get_input(self, input_key: str):
        for inp in self.inputs:
            if inp.key == input_key:
                return inp
        raise KeyError(f"Input {input_key} not found in component {self.label}")

    def get_component_example(self):
        if self.component_example_path is None:
            return None

        if not Path(self.component_example_path).is_file():
            return None
        try:
            with open(self.component_example_path, "r") as f:
                wf = json.load(f)
            return WorkflowModel.parse_obj(wf)
        except json.JSONDecodeError:
            return None

    def get_python_coder_deps(self):
        if self.class_name != PYTHON_CODER_NAME:
            return []

        coder_reqs = []
        for _inp in self.inputs:
            if _inp.data_type == DataType.CODE and _inp.value is not None:
                source_code_text = f"\n{_inp.value}"
                try:
                    coder_reqs.extend(
                        [
                            Requirement(imp)
                            for imp in get_imports(source_code=source_code_text)
                        ]
                    )
                except Exception as e:
                    raise ValueError(
                        f"Failed to parse requirements for {self.class_name} component. "
                        f"Please check the imports section: {str(e)}"
                    )
        return [r.line or r.name for r in coder_reqs]


class ComponentInputView(BaseModel):
    input_name: str
    data_type: str


class ComponentOutputView(BaseModel):
    data_type: str


class ComponentView(BaseModel):
    name: str
    description: str
    inputs: List[ComponentInputView]
    output: ComponentOutputView


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
        for dependency in value:
            try:
                if isinstance(dependency, dict):
                    dependency = ComponentDependency(**dependency)
                validated_dependencies.append(dependency)
            except ValueError as validation_error:
                cls.validation_invalid_errors.append(repr(validation_error))
                raise validation_error
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
                e = ValueError(
                    f"Either the source or the target of dependency {dep} not found in the components!"
                )
                self.invalid_errors.append(str(e))
                raise e

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
