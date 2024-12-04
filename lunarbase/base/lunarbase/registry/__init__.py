# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Union

from lunarbase.config import LunarConfig
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.llm_controller import LLMController
from lunarbase.registry.registry_models import RegisteredComponentModel, WorkflowRuntime
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from requirements.requirement import Requirement

import json

REGISTRY_LOGGER = setup_logger("lunarbase-registry")

CORE_COMPONENT_PATH = str(Path(Path(__file__).parent.parent.resolve(), "components"))


class LunarRegistry(BaseModel):
    REGISTER_BASE_COMMAND: ClassVar[List[str]] = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--no-input",
        "--isolated",
        "--no-deps",
        "--disable-pip-version-check",
        "--exists-action",
        "i",
        "-d",
    ]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    components: Optional[List[RegisteredComponentModel]] = Field(default_factory=list)
    workflow_runtime: Optional[List[WorkflowRuntime]] = Field(default_factory=list)
    config: Union[str, Dict, LunarConfig] = Field(default=...)
    persistence_layer: Optional[PersistenceLayer] = Field(default=None)

    datasource_controller: Optional[DatasourceController] = None
    llm_controller: Optional[LLMController] = None

    def get_workflow_runtime(self, workflow_id: str):
        for workflow in self.workflow_runtime:
            if workflow.workflow_id == workflow_id:
                return workflow
        return None

    def add_workflow_runtime(
        self, workflow_id: str, workflow_name: Optional[str] = None
    ):
        self.workflow_runtime.append(
            WorkflowRuntime(workflow_id=workflow_id, workflow_name=workflow_name)
        )

    def remove_workflow_runtime(self, workflow_id: str):
        self.workflow_runtime = [
            workflow
            for workflow in self.workflow_runtime
            if workflow.workflow_id != workflow_id
        ]

    def update_workflow_runtime(
        self,
        workflow_id: str,
        workflow_name: Optional[str] = None,
        workflow_pid: Optional[int] = None,
    ):
        for i, workflow in enumerate(self.workflow_runtime):
            if workflow.workflow_id == workflow_id:
                self.workflow_runtime[i].workflow_name = (
                    workflow_name or self.workflow_runtime[i].workflow_name
                )
                self.workflow_runtime[i].pid = (
                    workflow_pid or self.workflow_runtime[i].pid
                )
                return

    def get_by_class_name(self, class_name: str):
        for reg_comp in self.components:
            if reg_comp.component_model.class_name == class_name:
                return reg_comp
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
            self.persistence_layer.init_local_storage()

        if self.config is not None and len(self.components) == 0:
            REGISTRY_LOGGER.info(
                f"Trying to load cached registry from {self.config.REGISTRY_CACHE} ..."
            )
            try:
                with open(self.config.REGISTRY_CACHE, "r") as fd:
                    persisted_model = json.load(fd)

                self.components = []
                for persisted_component in persisted_model.get("components", []):
                    try:
                        registered_component = RegisteredComponentModel.model_validate(
                            persisted_component
                        )
                        # Cache the component_model
                        _ = registered_component.component_model
                        self.components.append(registered_component)

                    except ValueError as e:
                        REGISTRY_LOGGER.warn(
                            f"Failed to parse component {persisted_component}: {str(e)}! Skipping ..."
                        )
                REGISTRY_LOGGER.info(f"Loaded {len(self.components)} components.")
            except Exception as e:
                REGISTRY_LOGGER.warn(
                    f"Failed to load registry components from persistence layer: {str(e)}!"
                )
                self.components = []

        self.datasource_controller = DatasourceController(
            config=self.config, persistence_layer=self.persistence_layer
        )
        self.llm_controller = LLMController(
            config=self.config, persistence_layer=self.persistence_layer
        )

        return self

    async def register(self):
        _root = self.config.COMPONENT_LIBRARY_PATH
        if not Path(_root).is_dir():
            raise ValueError(f"Component root: {_root} not found!")
        REGISTRY_LOGGER.info(f"Running lunarverse registry ...")

        register_command = self.__class__.REGISTER_BASE_COMMAND + [_root, None]
        self.components = []
        with open(self.config.REGISTRY_FILE, "r") as fd:
            for component_line in fd:
                component_line = component_line.strip()
                try:
                    component_req = Requirement.parse(component_line)
                except ValueError:
                    warnings.warn(
                        f"Failed to parse component {component_line}."
                        f"Component will not be registered!"
                    )
                    continue

                register_command[-1] = component_line
                try:
                    REGISTRY_LOGGER.debug(f"Calling {' '.join(register_command)} ...")
                    _ = subprocess.run(
                        register_command,
                        capture_output=True,
                        text=True,
                        universal_newlines=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    warnings.warn(
                        f"Failed to download component {component_req.name} from {component_req.uri}: {e.stderr} ({e.returncode})."
                        f"Component will not be registered!"
                    )
                    continue
                except subprocess.TimeoutExpired:
                    warnings.warn(
                        f"Failed to download component {component_req.name} from {component_req.uri}: Timeout expired."
                        f"Component will not be registered!"
                    )
                    continue
                component_zip = glob.glob(f"{component_req.name}*.zip", root_dir=_root)
                if not component_zip or len(component_zip) == 0:
                    warnings.warn(
                        f"Failed to download component from {component_req.name} from {component_req.uri}: Unexpected package name."
                        f"Component will not be registered!"
                    )
                    continue

                if len(component_zip) > 1:
                    warnings.warn(
                        f"Multiple version of component {component_req.name} detected: {component_zip}."
                        f"Only the most recent will be registered!"
                    )
                    component_zip.sort(key=os.path.getmtime, reverse=True)
                component_zip = component_zip[0]
                zip_path = str(Path(_root, component_zip))

                REGISTRY_LOGGER.debug(
                    f"Registering component {component_req.name} from {zip_path}"
                )
                try:
                    registered_component = RegisteredComponentModel(
                        package_path=zip_path, module_name=component_req.name
                    )
                    # Cache the component_model
                    _ = registered_component.component_model
                    self.components.append(registered_component)

                except ValueError as e:
                    warnings.warn(
                        f"Failed to register external component in package {zip_path}! Details: {str(e)}. "
                        f"Component will not be registered!"
                    )
                    Path(zip_path).unlink(missing_ok=True)
                    continue

        REGISTRY_LOGGER.info(f"Registered {len(self.components)} external components.")
        _external_components = len(self.components)
        # SYSTEM COMPONENTS
        if Path(CORE_COMPONENT_PATH).is_dir():
            system_package_names = [
                pack.name
                for pack in Path(CORE_COMPONENT_PATH).iterdir()
                if pack.is_dir()
                and not pack.name.startswith("__")
                and not pack.name.startswith(".")
            ]

            for sys_pkg in system_package_names:
                zip_path = str(Path(_root, f"{sys_pkg}"))
                zip_path = shutil.make_archive(
                    zip_path, "zip", str(Path(CORE_COMPONENT_PATH, sys_pkg))
                )
                REGISTRY_LOGGER.debug(
                    f"Registering internal component {sys_pkg} from {zip_path}"
                )
                try:
                    registered_component = RegisteredComponentModel(
                        package_path=zip_path, module_name=sys_pkg
                    )
                    # Cache the component_model
                    _ = registered_component.component_model
                    self.components.append(registered_component)

                except ValueError as e:
                    warnings.warn(
                        f"Failed to register internal component in package {zip_path}! Details: {str(e)}. "
                        f"Component will not be registered!"
                    )
                    Path(zip_path).unlink(missing_ok=True)
                    continue

        REGISTRY_LOGGER.info(
            f"Registered {len(self.components) - _external_components} system components."
        )
        await self.save()

    async def save(self):
        _model = self.model_dump(exclude={"persistence_layer", "datasource_controller", "llm_controller"})
        saved_to = await self.persistence_layer.save_to_storage_as_json(
            path=self.config.REGISTRY_CACHE, data=_model
        )
        return saved_to

    def get_component_names(self):
        return [comp.component_model.name for comp in self.components]

    def get_data_source(self, datasource_id: str):
        current_user = os.environ.get("LUNAR_USERID", None)
        if current_user is None:
            REGISTRY_LOGGER.warn(
                f"User not set! Cannot access data source {datasource_id}!"
            )
            return None

        ds = self.datasource_controller.get_datasource(
            user_id=current_user, filters={"id": datasource_id}
        )
        if len(ds) > 0:
            ds = ds[0]
        return ds

    def get_llm(self, llm_id: str):
        current_user = os.environ.get("LUNAR_USERID", None)
        if current_user is None:
            REGISTRY_LOGGER.warn(f"User not set! Cannot access LLM {llm_id}!")
            return None
        llm = self.llm_controller.get_llm(user_id=current_user, filters={"id": llm_id})
        if len(llm) > 0:
            llm = llm[0]
        return llm

    def get_user_context(self):
        current_user = os.environ.get("LUNAR_USERID", None)
        if current_user is None:
            REGISTRY_LOGGER.warn(f"User not set!")
            return None

        return {
            "workflow_root": self.persistence_layer.get_user_workflow_root(current_user),
            "datasource_root": self.persistence_layer.get_user_datasource_root(
                current_user
            ),
            "llm_root": self.persistence_layer.get_user_llm_root(current_user),
            "file_root": self.persistence_layer.get_user_file_root(current_user),
            "component_index": self.persistence_layer.get_user_component_index(
                current_user
            ),
            "workflow_index": self.persistence_layer.get_user_workflow_index(
                current_user
            ),
            "custom_root": self.persistence_layer.get_user_custom_root(current_user),
            "tmp": self.persistence_layer.get_user_tmp(current_user),
            "environment": self.persistence_layer.get_user_environment_path(current_user),
        }




