# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import os
import shutil
import subprocess
import sys
import traceback
from urllib.parse import urlparse
import warnings
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Union

from lunarbase.config import LunarConfig
from lunarbase.controllers.configuration_profile_controller import (
    ConfigurationProfileController,
)
from lunarbase.registry.registry_models import (
    ConfiguredComponentModel,
    PythonIntegrationModel,
    WorkflowRuntime,
)
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from requirements.requirement import Requirement

import json

REGISTRY_LOGGER = setup_logger("lunarbase-registry")

CORE_COMPONENT_PATH = str(Path(Path(__file__).parent.parent.resolve(), "components"))


class LunarRegistry(BaseModel):
    REGISTER_COPY_COMMAND: ClassVar[List[str]] = [
        "cp",
        "-a",
    ]
    REGISTER_DOWNLOAD_COMMAND: ClassVar[List[str]] = [
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
    # Union typing necessary, otherwise Pydantic model_dump (and maybe other methods) will fail to apply polymorphism
    components: Optional[
        List[Union[ConfiguredComponentModel, PythonIntegrationModel]]
    ] = Field(default_factory=list)
    workflow_runtime: Optional[List[WorkflowRuntime]] = Field(default_factory=list)
    config: Union[str, Dict, LunarConfig] = Field(default=...)
    persistence_layer: Optional[PersistenceLayer] = Field(default=None)

    configuration_profile_controller: Optional[ConfigurationProfileController] = None

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
                        if persisted_component.get("external", False):
                            # Python integration is assumed
                            registered_component = (
                                PythonIntegrationModel.model_validate(
                                    persisted_component
                                )
                            )

                        else:
                            registered_component = (
                                ConfiguredComponentModel.model_validate(
                                    persisted_component
                                )
                            )
                        # Cache the component_model
                        _ = registered_component.component_model
                        self.components.append(registered_component)

                    except ValueError as e:
                        REGISTRY_LOGGER.warning(
                            f"Failed to parse component {persisted_component}: {str(e)}! Skipping ..."
                        )
                REGISTRY_LOGGER.info(f"Loaded {len(self.components)} components.")
            except FileNotFoundError:
                REGISTRY_LOGGER.warning("No cached registry found.")

            except Exception as e:
                # REGISTRY_LOGGER.warning(
                #     f"Failed to load registry components from persistence layer: {str(e)}!"
                # )
                # self.components = []
                REGISTRY_LOGGER.error(
                    "Failed to load registry components from persistence layer"
                )
                raise e

        self.configuration_profile_controller = ConfigurationProfileController(
            config=self.config, persistence_layer=self.persistence_layer
        )
        return self

    def register_python_integration(self, integration_path: Union[os.PathLike, str]):
        if isinstance(integration_path, str):
            integration_path = Path(integration_path)

        if (
            not integration_path.exists()
            or not integration_path.is_file()
            or not integration_path.name.endswith(".json")
        ):
            raise ValueError(
                f"Integration {integration_path} not found or is not a JSON file!"
            )

        try:
            with open(integration_path, "r") as integration_file:
                integration_model = json.load(integration_file)
                integration_model = PythonIntegrationModel.model_validate(
                    integration_model
                )
                return integration_model
        except Exception as e:
            REGISTRY_LOGGER.error(
                f"Failed to load integration from {integration_path}: {str(e)}"
            )
            raise e

    def register(self):
        _root = self.config.COMPONENT_LIBRARY_PATH
        if not Path(_root).is_dir():
            raise ValueError(f"Component root: {_root} not found!")
        REGISTRY_LOGGER.info("Running lunarverse registry ...")

        self.components = []
        with open(self.config.REGISTRY_FILE, "r") as fd:
            for component_line in fd:
                component_line = component_line.strip()
                REGISTRY_LOGGER.info(f"Processing component {component_line} ...")
                if component_line.startswith("integration://"):
                    integration_path = urlparse(component_line).path or None
                    if integration_path is None:
                        warnings.warn(
                            f"No path found in integration {component_line}! Skipping ..."
                        )
                        continue
                    integration_path = Path(integration_path)
                    if not integration_path.exists():
                        warnings.warn(
                            f"Integration {integration_path} not found! Skipping ..."
                        )
                        continue
                    try:
                        integration_model = self.register_python_integration(
                            integration_path
                        )
                        self.components.append(integration_model)
                        REGISTRY_LOGGER.info(
                            f"Registered integration {integration_path}!"
                        )
                        continue
                    except Exception as e:
                        warnings.warn(
                            f"Failed to register integration {integration_path}: {str(e)}"
                        )
                        continue

                try:
                    component_req = Requirement.parse(component_line)
                    if component_req.local_file and component_req.name is None:
                        component_req.path = urlparse(component_req.uri).path
                        if Path(component_req.path).exists():
                            component_req.name = Path(component_req.path).name

                except ValueError:
                    warnings.warn(
                        f"Failed to parse component {component_line}."
                        f"Component will not be registered!"
                    )
                    continue

                REGISTRY_LOGGER.info(
                    f"Downloading component {component_req.name} @ {component_req.uri}"
                )

                try:
                    if component_req.local_file:
                        register_command = self.__class__.REGISTER_COPY_COMMAND + [
                            component_req.path,
                            f"{_root}/{component_req.name}",
                        ]
                    else:
                        register_command = self.__class__.REGISTER_DOWNLOAD_COMMAND + [
                            _root,
                            component_line,
                        ]

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
                        f"Failed to download component {component_req.name} from {component_req.uri}:"
                        f"{e.stderr} ({e.returncode})."
                        f"Component will not be registered!"
                    )
                    continue
                except subprocess.TimeoutExpired:
                    warnings.warn(
                        f"Failed to download component {component_req.name} from {component_req.uri}: Timeout expired."
                        f"Component will not be registered!"
                    )
                    continue

                if component_req.local_file:
                    shutil.make_archive(
                        f"{_root}/{component_req.name}", "zip", component_req.path
                    )
                    shutil.rmtree(f"{_root}/{component_req.name}", ignore_errors=True)

                component_zip = glob.glob(f"{component_req.name}*.zip", root_dir=_root)
                if not component_zip or len(component_zip) == 0:
                    warnings.warn(
                        f"Failed to download component {component_req.name} from {component_req.uri}:"
                        "Unexpected package name."
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

                REGISTRY_LOGGER.info(
                    f"Registering component {component_req.name} from {zip_path}"
                )
                try:
                    registered_component = ConfiguredComponentModel(
                        package_path=zip_path, module_name=component_req.name
                    )
                    # Cache the component_model
                    _ = registered_component.component_model
                    self.components.append(registered_component)

                except ValueError:
                    warnings.warn(
                        f"Failed to register component in package {zip_path}! Details: {traceback.format_exc()}."
                        f"Component will not be registered!"
                    )
                    Path(zip_path).unlink(missing_ok=True)
                    continue
        REGISTRY_LOGGER.info(f"Registered {len(self.components)} components.")

        for pkg in os.listdir(CORE_COMPONENT_PATH):
            pkg_path = Path(CORE_COMPONENT_PATH, pkg)
            if not pkg_path.is_dir():
                continue

            if not Path(pkg_path, "__init__.py").exists():
                continue

            self.components.append(
                ConfiguredComponentModel(package_path=str(pkg_path), module_name=pkg)
            )

        self.save()

    def save(self):
        _model = self.model_dump(
            mode="json",
            exclude_defaults=False,
            exclude={"persistence_layer", "configuration_profile_controller"},
        )
        saved_to = self.persistence_layer.save_to_storage_as_json(
            path=self.config.REGISTRY_CACHE, data=_model
        )
        return saved_to

    def get_component_names(self):
        return [comp.component_model.name for comp in self.components]

    def get_config_profile(self, config_profile_id: str):
        current_user = os.environ.get("LUNAR_USERID", None)
        if current_user is None:
            warnings.warn("User not set! Cannot access configuration profiles!")
            return None

        config_profiles = (
            self.configuration_profile_controller.get_configuration_profile(
                user_id=current_user, filters={"id": config_profile_id}
            )
        )
        if len(config_profiles) > 0:
            config_profiles = config_profiles[0]
        return config_profiles

    def get_user_context(self):
        current_user = os.environ.get("LUNAR_USERID", None)
        if current_user is None:
            REGISTRY_LOGGER.warning("User not set!")
            return None

        return {
            "workflow_root": self.persistence_layer.get_user_workflow_root(
                current_user
            ),
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
            "environment": self.persistence_layer.get_user_environment_path(
                current_user
            ),
        }
