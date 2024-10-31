# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import ast
import errno
import json
import os
import re
import shutil
import warnings
from pathlib import Path
from typing import Dict, Optional, Union

import git
from lunarbase.config import COMPONENT_EXAMPLE_WORKFLOW_NAME, GLOBAL_CONFIG, LunarConfig
from lunarbase.persistence import PersistenceLayer
from lunarbase.registry.registree_model import ComponentRegistree
from lunarcore.component.lunar_component import (
    COMPONENT_DESCRIPTION_TEMPLATE,
    LunarComponent,
)
from lunarbase.modeling.data_models import (
    ComponentInput,
    ComponentModel,
    ComponentOutput,
    WorkflowModel,
)
from lunarbase.utils import setup_logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

# TODO: Allow installable components rather than code

BASE_COMPONENT_CLASS_NAME = LunarComponent.__name__

REGISTRY_LOGGER = setup_logger("lunarbase-registry")

CORE_COMPONENT_PATH = (Path(__file__).parent.parent.resolve() / "components").as_posix()


class ComponentRegistry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    components: Optional[Dict] = Field(default_factory=dict)
    config: Union[str, Dict, LunarConfig] = Field(default=GLOBAL_CONFIG)
    persistence_layer: Optional[PersistenceLayer] = Field(default=None)

    def get_by_class_name(self, class_name: str):
        """
        TODO: Maybe a lazy loading/registering for components here?
        """
        for pkg, comp in self.components.items():
            if comp.class_name == class_name:
                return pkg, comp
        return None

    @field_validator("config")
    @classmethod
    def validate_config(cls, value):
        if isinstance(value, str):
            value = LunarConfig.get_config(settings_file_path=value)
        elif isinstance(value, dict):
            value = LunarConfig.model_validate(value)
        return value

    @model_validator(mode="after")
    def validate_model(self):
        if self.config is not None and self.persistence_layer is None:
            self.persistence_layer = PersistenceLayer(config=self.config)
        return self

    @staticmethod
    def generate_component_model(path: str):
        if not os.path.isdir(path):
            raise ValueError(f"Path {path} not found!")

        main_class = os.path.join(path, "__init__.py")
        try:
            with open(os.path.abspath(main_class), "r") as f:
                source_code = f.read()
        except FileNotFoundError:
            warnings.warn(
                f"Path {main_class} not found! Component will not be indexed!"
            )
            return None

        tree = ast.parse(source_code)
        component_class_defs = [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        if len(component_class_defs) < 1:
            warnings.warn(
                f"A component definition must inherit from {BASE_COMPONENT_CLASS_NAME} and be placed in component_group.py. "
                f"Class at {main_class} contains {len(component_class_defs)} classes. Component will not be indexed!"
            )
            return None

        component_class, component_class_name = None, None
        base_class_names = set()
        for _cls in component_class_defs:
            base_class_names = {b.id for b in _cls.bases}
            if BASE_COMPONENT_CLASS_NAME in base_class_names:
                component_class = _cls
                component_class_name = _cls.name
                break

        if (
            component_class_name is None
            or BASE_COMPONENT_CLASS_NAME not in base_class_names
        ):
            warnings.warn(
                f"A class in {main_class} must inherit {BASE_COMPONENT_CLASS_NAME}. Component will not be indexed!"
            )
            return None

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
                component_code=r"{}".format(os.path.abspath(main_class)),
                configuration={"force_run": False, **keywords},
            )
            inputs = [
                ComponentInput(
                    key=_in_name, data_type=_in_type, component_id=component_model.id
                )
                for _in_name, _in_type in input_types
            ]
            component_model.inputs = inputs

        except KeyError as e:
            warnings.warn(
                f"Failed to parse component at {main_class}! One or more expected attributes may be missing. Details: {str(e)}. Component will not be indexed!"
            )
            return None

        return component_model

    def fetch(self, registry_path: str):
        if not os.path.isfile(registry_path):
            raise ValueError(
                f"Cannot fetch components from {registry_path}: No such file!"
            )

        component_cache = {comp.name for _, comp in self.components.items()}
        current_components = {comp.name for comp in component_cache}
        with open(registry_path, "r") as fd:
            raw_register_data = json.load(fd)

        for reg_obj in raw_register_data:
            REGISTRY_LOGGER.debug(
                f"Fetching component {reg_obj['name']} from {reg_obj['location']}."
            )
            reg_obj.update(
                {
                    "github_token": reg_obj.get("github_token")
                    or self.config.REGISTRY_GITHUB_TOKEN
                }
            )
            try:
                reg_obj = ComponentRegistree.model_validate(reg_obj)
            except ValueError as e:
                warnings.warn(
                    f"Failed to parse component information \n{reg_obj}\n. {str(e)} \n"
                    f"Component not registered!"
                )
                continue
            if reg_obj.name in current_components:
                warnings.warn(
                    f"A component with name {reg_obj.name} is already registered."
                    f"Please rename the new component to register it!"
                )
                continue

            dst = os.path.join(
                self.config.COMPONENT_LIBRARY_PATH, reg_obj.name.replace("-", "_")
            )

            if (
                os.path.isdir(dst)
                and len(os.listdir(dst)) > 0
                and not self.config.REGISTRY_ALWAYS_UPDATE
            ):
                continue

            if reg_obj.is_local:
                src = reg_obj.location
                if reg_obj.subdirectory is not None:
                    src = os.path.join(reg_obj.location, reg_obj.subdirectory)

                if src == dst:
                    continue
                try:
                    os.makedirs(dst, exist_ok=True)
                    os.symlink(src, os.path.join(dst, reg_obj.name.replace("-", "_")))
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        os.remove(os.path.join(dst, reg_obj.name.replace("-", "_")))
                        os.symlink(
                            src, os.path.join(dst, reg_obj.name.replace("-", "_"))
                        )
                    else:
                        warnings.warn(
                            f"Failed to create link for component {reg_obj.name}: {str(e)}. Skipping ..."
                        )
                        if os.path.exists(dst) and os.path.isdir(dst):
                            shutil.rmtree(dst)

                        continue

            else:
                try:
                    repo = git.Repo.init(dst)
                    try:
                        origin = repo.remotes[0]
                    except IndexError:
                        origin = repo.create_remote("origin", reg_obj.location)
                    origin.fetch()

                    repo = repo.git()
                    if reg_obj.subdirectory is not None:
                        repo.checkout(
                            f"origin/{reg_obj.branch}", "--", reg_obj.subdirectory
                        )
                    else:
                        repo.checkout(f"origin/{reg_obj.branch}")
                except Exception as e:
                    warnings.warn(
                        f"Failed to fetch component {reg_obj.name}: {str(e)}. Skipping ..."
                    )
                    if os.path.exists(dst) and os.path.isdir(dst):
                        shutil.rmtree(dst)
                    continue

    async def register(self, fetch: bool = True, exemple: bool = True):
        _root = self.config.COMPONENT_LIBRARY_PATH
        if not os.path.isdir(_root):
            raise ValueError(f"Path {_root} not found!")
        REGISTRY_LOGGER.info(f"Running registry with fetch set to {fetch}.")
        if fetch:
            self.fetch(self.config.PERSISTENT_REGISTRY_STARTUP_FILE)

        package_names = [
            pack
            for pack in os.listdir(_root)
            if os.path.isdir(os.path.join(_root, pack))
            and not pack.startswith("__")
            and not pack.startswith(".")
        ]
        package_names = [os.path.join(_root, pkg, pkg) for pkg in package_names]

        system_package_names = []
        if os.path.isdir(CORE_COMPONENT_PATH):
            system_package_names = [
                pack
                for pack in os.listdir(CORE_COMPONENT_PATH)
                if os.path.isdir(os.path.join(CORE_COMPONENT_PATH, pack))
                and not pack.startswith("__")
                and not pack.startswith(".")
            ]
        system_package_names = [
            os.path.join(CORE_COMPONENT_PATH, pkg) for pkg in system_package_names
        ]

        for pkg in package_names + system_package_names:
            REGISTRY_LOGGER.debug(f"Registering component from {pkg}.")
            try:
                cmp = ComponentRegistry.generate_component_model(pkg)
            except Exception as e:
                warnings.warn(
                    f"Failed to parse component in package {pkg}! Details: {str(e)}. Component will not be indexed!"
                )
                continue

            if cmp is None:
                continue

            cmp_key = os.path.dirname(
                os.path.relpath(cmp.component_code, self.config.COMPONENT_LIBRARY_PATH)
            )
            self.components[cmp_key.replace("/", ".")] = cmp

            if exemple:
                example_location = os.path.join(pkg, COMPONENT_EXAMPLE_WORKFLOW_NAME)
                if os.path.isfile(example_location):
                    continue
                workflow = WorkflowModel(
                    user_id="",
                    name=f"{cmp.name} component example",
                    description=f"A one-component workflow illustrating the use of {cmp.name} component.",
                    components=[cmp],
                )
                workflow_dict = workflow.model_dump()
                with open(example_location, "w") as f:
                    json.dump(workflow_dict, f, indent=4)

        REGISTRY_LOGGER.info(f"Registered {len(package_names)} components.")

        if fetch:
            await self.save()

        return self

    async def save(self):
        _model = self.model_dump(exclude={"persistence_layer"})
        saved_to = await self.persistence_layer.save_to_storage_as_json(
            path=self.config.PERSISTENT_REGISTRY_NAME, data=_model
        )
        return saved_to

    async def load_components(self):
        REGISTRY_LOGGER.info(
            f"Trying to load cached registry from {self.config.PERSISTENT_REGISTRY_NAME} ..."
        )
        try:
            persisted_model = await self.persistence_layer.get_from_storage_as_dict(
                path=self.config.PERSISTENT_REGISTRY_NAME
            )

            self.components = dict()
            for comp_path, comp_dict in persisted_model.get(
                "components", dict()
            ).items():
                try:
                    comp_model = ComponentModel.model_validate(comp_dict)
                    self.components[comp_path] = comp_model
                except ValueError as e:
                    REGISTRY_LOGGER.warn(
                        f"Failed to parse component {comp_dict}: {str(e)}! Skipping ..."
                    )
            REGISTRY_LOGGER.info(f"Loaded {len(self.components)} components.")
        except ValueError as e:
            REGISTRY_LOGGER.warn(
                f"Failed to load registry components from persistence layer: {str(e)}!"
            )
            self.components = dict()

    def get_component_names(self):
        return [comp.name for _, comp in self.components]
