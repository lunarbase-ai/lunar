from abc import abstractmethod
import ast
import functools
import importlib
import json
import re
import zipfile
from functools import cached_property
from pathlib import Path
from time import time
from typing import Any, Dict, Optional, List
from uuid import uuid4

from lunarbase.components.errors import ComponentError
import requirements
from autoimport import fix_code
from lunarcore.component.lunar_component import (
    LunarComponent,
    COMPONENT_DESCRIPTION_TEMPLATE,
)
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    computed_field,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo
from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentOutput,
    ComponentInput,
)

from lunarbase.utils import to_camel, anyinzip, anyindir
from requirements.requirement import Requirement

from lunarcore.component.data_types import DataType

REQ_FILE_NAME = "requirements.txt"


class RegisteredComponentModel(BaseModel):
    # Base class for registered components
    external: bool = Field(
        default=None, description="Whether the integration is external or not."
    )
    component_requirements: List[str] = Field(
        default_factory=list, validate_default=True
    )

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_attributes_allowed = True
        validate_assignment = True

    @field_validator("component_requirements")
    @classmethod
    def validate_component_requirements(cls, value):
        for i, spec in enumerate(value):
            try:
                spec = Requirement(spec)
                value[i] = spec.line or spec.name
            except Exception as e:
                raise ValueError(
                    f"Failed to parse requirement {spec} "
                    f"The component may not work. Please follow common requirements.txt rules! Details: {str(e)}"
                )
        return value

    @abstractmethod
    def component_model(self):
        pass


class ExternalIntegrationModel(RegisteredComponentModel):
    # Base class for external integrations
    name: str = Field(..., description="The name of the integration.")
    description: Optional[str] = Field(
        default=None, description="The description of the integration."
    )
    group: Optional[str] = Field(
        default="Integrations", description="The group of the integration."
    )
    documentation_url: Optional[str] = Field(
        default=None, description="The URL to the documentation for the integration."
    )
    external: bool = Field(
        default=True, description="Whether the integration is external or not."
    )

    @abstractmethod
    def assemble(self):
        pass


class PythonIntegrationModel(ExternalIntegrationModel):
    # TODO: Support for Github integration
    package: Optional[str] = Field(
        default=None, description="The name of a PyPI package or a local package."
    )
    package_version: Optional[str] = Field(
        default=None, description="The version of the package."
    )

    module_path: str = Field(
        default=..., description="The module path to the integration."
    )

    class_name: Optional[str] = Field(
        default=None, description="The class from the module to instantiate."
    )
    class_args: Optional[Dict] = Field(
        default_factory=dict, description="The arguments to pass to the class instance."
    )

    entry_point: str = Field(
        default=..., description="The main method to call when using the integration."
    )

    entry_point_args: Optional[Dict] = Field(
        default_factory=dict, description="The arguments to pass to the main method."
    )

    entry_point_result_type: Optional[str] = Field(
        default=..., description="The return type of the main method."
    )

    entry_point_result_serializer: Optional[str] = Field(
        default=None,
        description="The serializer to use for the return type of the main method. This assumed the output is an object with this method.",
    )

    @field_validator("class_args")
    @classmethod
    def validate_class_args(cls, value):
        for arg_key, arg_type in value.items():
            if not isinstance(arg_type, str):
                continue
            try:
                arg_type = DataType[arg_type.upper()]
            except KeyError:
                arg_type = DataType(arg_type)
            value[arg_key] = arg_type
        return value

    @field_validator("entry_point_args")
    @classmethod
    def validate_entry_point_args(cls, value):
        for arg_key, arg_type in value.items():
            if not isinstance(arg_type, str):
                continue
            try:
                arg_type = DataType[arg_type.upper()]
            except KeyError:
                arg_type = DataType(arg_type)
            value[arg_key] = arg_type
        return value

    @field_validator("entry_point_result_type")
    @classmethod
    def validate_entry_point_result_type(cls, value):
        if not isinstance(value, str):
            return value
        try:
            value = DataType[value.upper()]
        except KeyError:
            value = DataType(value)
        return value

    @field_serializer("entry_point_args", when_used="always")
    def serialize_entry_point_args(value):
        for arg_key, arg_type in value.items():
            if not isinstance(arg_type, DataType):
                continue
            value[arg_key] = arg_type.value
        return value

    @field_serializer("class_args", when_used="always")
    def serialize_class_args(value):
        for arg_key, arg_type in value.items():
            if not isinstance(arg_type, DataType):
                continue
            value[arg_key] = arg_type.value
        return value

    @field_serializer("entry_point_result_type", when_used="always")
    def serialize_entry_point_result_type(value):
        if isinstance(value, DataType):
            return value.value
        return value

    @model_validator(mode="after")
    def validate_integration(self):
        if self.description is None:
            self.description = f"A component that implements the functionality of {self.entry_point} from {self.module_path}."
        if self.package is None:
            raise ValueError(
                "Either a pypi package or a local package path must be provided."
            )

        if self.entry_point is None or self.module_path is None:
            raise ValueError("entry_point and module_path must be provided.")

        return self

    @staticmethod
    def integration_constructor(
        self_,
        configuration: Optional[Dict] = None,
    ):
        super(self_.__class__, self_).__init__(configuration=configuration)

    @staticmethod
    def integration_run(
        module: str,
        entry_point: str,
        class_name: Optional[str] = None,
        class_args: Optional[List] = None,
        result_serializer: Optional[str] = None,
        **inputs: Any,
    ):
        def serialize_result(result: Any, serializer: Optional[str] = None):
            if serializer is None:
                return result
            try:
                _ = iter(result)
            except TypeError:
                serializer = getattr(result, serializer)
                return serializer()
            mapped_result = map(lambda x: getattr(x, serializer)(), result)
            return type(result)(mapped_result)

        try:
            integration_module = importlib.import_module(module)
        except ImportError as e:
            raise ComponentError(f"Failed to import module {module}: {e}")

        if class_name is not None:
            integration_class = getattr(integration_module, class_name)
            try:
                integration_entry_point = getattr(integration_class, entry_point)
                _entry_point_expected_args = (
                    integration_entry_point.__code__.co_varnames
                )
                if (
                    len(_entry_point_expected_args) == 0
                    or _entry_point_expected_args[0].lower() == "cls"
                ):
                    integration_results = integration_entry_point(**inputs)
                    return serialize_result(integration_results, result_serializer)

                if not all([ca in inputs for ca in class_args]):
                    raise ComponentError(
                        f"Integration class {class_name} requires {class_args} but only {inputs.keys()} provided."
                    )
                class_args = {ca: inputs.pop(ca) for ca in class_args or []}
                integration_instance = integration_class(**class_args)
                integration_results = getattr(integration_instance, entry_point)(
                    **inputs
                )
                return serialize_result(integration_results, result_serializer)
            except AttributeError as e:
                raise ComponentError(
                    f"Integration class {class_name} has no attribute {entry_point}: {e}"
                )
        else:
            integration_instance = None
            try:
                integration_entry_point = getattr(integration_module, entry_point)
            except AttributeError as e:
                raise ComponentError(
                    f"Integration module {integration_module} has no attribute {entry_point}: {e}"
                )
            integration_results = integration_entry_point(**inputs)
            return serialize_result(integration_results, result_serializer)

    def assemble(self):
        inputs = self.class_args or dict()
        inputs.update(self.entry_point_args or dict())

        integration_class = type(
            f"{self.class_name}LunarIntegration",
            (LunarComponent,),
            {
                "__init__": self.__class__.integration_constructor,
                "run": functools.partial(
                    self.__class__.integration_run,
                    module=self.module_path,
                    entry_point=self.entry_point,
                    class_name=self.class_name,
                    class_args=list(self.class_args.keys()),
                    result_serializer=self.entry_point_result_serializer,
                ),
            },
            component_name=self.name,
            component_description=self.description,
            input_types=inputs,
            output_type=self.entry_point_result_type,
            component_group=self.group,
        )

        # Return the assembled class
        return integration_class

    @computed_field(return_type=ComponentModel)
    @cached_property
    def component_model(self):
        _assembled = self.assemble()

        component_model = ComponentModel(
            name=_assembled.component_name,
            label=None,
            class_name=_assembled.__name__,
            description=_assembled.component_description,
            group=_assembled.component_group,
            inputs=[],
            output=ComponentOutput(data_type=_assembled.output_type),
            configuration={"force_run": False},
        )
        inputs = [
            ComponentInput(
                key=_in_name,
                data_type=_in_type,
                component_id=component_model.id,
            )
            for _in_name, _in_type in _assembled.input_types.items()
        ]
        component_model.inputs = inputs
        return component_model

    @model_validator(mode="after")
    def validate_component_model(self):
        if Path(self.package).is_dir():
            self.component_requirements.append(f"file://{self.package}")
        elif self.package_version is not None:
            self.component_requirements.append(
                f"{self.package} == {self.package_version}"
            )
        else:
            self.component_requirements.append(self.package)
        return self


class ConfiguredComponentModel(RegisteredComponentModel):
    package_path: str = Field(default=...)
    module_name: str = Field(default=...)

    external: bool = Field(
        default=False, description="Whether the integration is external or not."
    )

    @property
    def is_zip_package(self):
        return zipfile.is_zipfile(self.package_path)

    @field_validator("package_path")
    @classmethod
    def validate_package_path(cls, value):
        if not Path(value).exists():
            raise ValueError(f"No such file or directory: {value}!")
        return value

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value, info: ValidationInfo):
        _package_path = info.data.get("package_path")

        class_path_candidates = [
            str(Path(value, "src", value, "__init__.py")),
            str(Path("src", value, "__init__.py")),
            str(Path(value, "__init__.py")),
            "__init__.py",
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

    # @field_validator("component_requirements")
    # @classmethod
    # def validate_component_code_requirements(cls, value, info: ValidationInfo):

    @model_validator(mode="after")
    def validate_component_model(self):
        _component_code = self.package_path
        _module_name = self.module_name
        reqs = []

        if zipfile.is_zipfile(_component_code):
            with zipfile.ZipFile(_component_code) as z:
                try:
                    req_text = z.read(REQ_FILE_NAME).decode("utf-8")
                    for line in req_text.split("\n"):
                        if line.startswith("#"):
                            continue
                        line = line.strip()
                        if len(line) == 0:
                            continue
                        try:
                            reqs.extend(list(requirements.parse(line)))

                        except Exception as e:
                            raise ValueError(
                                f"Failed to parse requirement {line} for component {_module_name}. "
                                "This component may not work. Please follow common requirements.txt rules! "
                                f"Details: {str(e)}"
                            )
                except KeyError:
                    pass
        else:
            req_file_path = Path(_component_code).parent
            req_file_path = Path(req_file_path, REQ_FILE_NAME)
            if req_file_path.is_file():
                with open(str(req_file_path), "r") as fd:
                    for line in fd:
                        if line.startswith("#"):
                            continue
                        line = line.strip()
                        if len(line) == 0:
                            continue
                        try:
                            reqs.extend(list(requirements.parse(line)))
                        except Exception as e:
                            raise ValueError(
                                f"Failed to parse requirement {line} for component {_module_name}. "
                                "This component may not work. Please follow common requirements.txt rules! "
                                f"Details: {str(e)}"
                            )

        self.component_requirements.extend(
            [f"{_module_name} @ file://{_component_code}"]
            + list({r.line or r.name for r in reqs})
        )
        return self

    @computed_field(return_type=ComponentModel)
    @cached_property
    def component_model(self):
        class_path_candidates = [
            str(Path(self.module_name, "src", self.module_name, "__init__.py")),
            str(Path("src", self.module_name, "__init__.py")),
            str(Path(self.module_name, "__init__.py")),
            "__init__.py",
        ]
        if self.is_zip_package:
            class_path = anyinzip(self.package_path, class_path_candidates)
            with zipfile.ZipFile(self.package_path) as z:
                source_code = z.read(class_path).decode("utf-8")
        else:
            class_path = anyindir(self.package_path, class_path_candidates)
            with open(str(Path(self.package_path, class_path)), "r") as f:
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
                f"Main class in {self.package_path} must inherit {LunarComponent.__name__}!"
            )

        keywords = ",".join(
            [f'"{kw.arg}": {ast.unparse(kw.value)}' for kw in component_class.keywords]
        )

        keywords = re.sub(r"(?<!\w)\'|\'(?!\w)", '"', keywords)
        keywords = re.sub(r"DataType\.(\w+)", r'"\1"', keywords)
        keywords = re.sub(r"DataSourceType\.(\w+)", r'"\1"', keywords)
        keywords = re.sub(r"ComponentGroup\.(\w+)", r'"\1"', keywords)
        keywords = re.sub(r":\s?(None)", r':"\1"', keywords)
        keywords = json.loads("{" + keywords + "}")

        _component_description = keywords.pop("component_description", None)
        if _component_description is None or _component_description == "":
            _component_description = COMPONENT_DESCRIPTION_TEMPLATE

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
