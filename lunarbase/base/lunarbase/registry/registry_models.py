import ast
import json
import re
import zipfile
from functools import cached_property
from pathlib import Path
from time import time
from typing import Optional, List, Dict
from uuid import uuid4

import requirements
from autoimport import fix_code
from lunarcore.component.lunar_component import (
    LunarComponent,
    COMPONENT_DESCRIPTION_TEMPLATE,
)
from pydantic import BaseModel, Field, field_validator, computed_field
from pydantic_core.core_schema import ValidationInfo

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentOutput,
    ComponentInput,
)

from lunarbase.utils import to_camel, anyinzip, anyindir
from requirements.requirement import Requirement

REQ_FILE_NAME = "requirements.txt"


class RegisteredComponentModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_attributes_allowed = True
        validate_assignment = True

    package_path: str = Field(default=...)
    module_name: str = Field(default=...)
    component_requirements: List[str] = Field(default_factory=list)

    @property
    def is_zip_package(self):
        return zipfile.is_zipfile(self.package_path)

    @field_validator("package_path")
    @classmethod
    def validate_package_path(cls, value):
        if not Path(value).is_file() or Path(value).is_dir():
            raise ValueError(f"No such file or directory: {value}!")
        return value

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value, info: ValidationInfo):
        _package_path = info.data.get("package_path")

        class_path_candidates = [
            str(Path(value, "src", value, "__init__.py")),
            str(Path("src", value, "__init__.py")),
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

    @field_validator("component_requirements")
    @classmethod
    def validate_component_code_requirements(cls, value, info: ValidationInfo):
        _component_code = info.data.get("package_path")
        _module_name = info.data.get("module_name")
        reqs = []

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
            req_file_path = Path(_component_code).parent
            req_file_path = Path(req_file_path, REQ_FILE_NAME)
            if req_file_path.is_file():
                with open(str(req_file_path), "r") as fd:
                    try:
                        reqs.extend([req for req in requirements.parse(fd)])
                    except Exception as e:
                        raise ValueError(
                            f"Failed to parse requirements for component {info.data['name']}. "
                            f"This component may not work. Please follow common requirements.txt rules! Details: {str(e)}"
                        )

        # return [r.name or r.line for r in reqs if importlib.util.find_spec(r.name or r.line or "") is None]
        return [f"{_module_name} @ file://{_component_code}"] + list(
            {r.line or r.name for r in reqs}
        )

    @computed_field(return_type=ComponentModel)
    @cached_property
    def component_model(self):
        class_path_candidates = [
            str(Path(self.module_name, "src", self.module_name, "__init__.py")),
            str(Path("src", self.module_name, "__init__.py")),
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

        # We can assume all source imports ar captured in the requirements.txt
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
                # component_code=self.package_path,
                # component_code_requirements=[
                #     f"{self.module_name} @ file://{self.package_path}"
                # ],
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

    @computed_field(return_type=Dict)
    @cached_property
    def view(self):
        return {
            "name": self.component_model.class_name,
            "description": self.component_model.description,
            "inputs": [
                {
                    "name": _in.key,
                    "data_type": _in.data_type,
                }
                for _in in self.component_model.inputs
            ],
            "output": {
                "data_type": self.component_model.output.data_type,
            },
        }



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
