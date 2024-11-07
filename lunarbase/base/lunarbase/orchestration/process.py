# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import os.path
import subprocess
import sys
import warnings
from functools import lru_cache
from io import StringIO
from typing import Any, ClassVar, Dict, List, Optional
from venv import EnvBuilder

from dotenv import dotenv_values
from prefect.infrastructure.process import Process
from prefect.utilities.processutils import run_process
# This is because Prefect's Infrastructure is still using Pydantic V1
from pydantic.v1 import Field, root_validator, validator
from requirements.parser import parse


def create_venv_builder():
    # need system_site_packages=True inside docker
    # system_site_packages = Path("/app/in_docker").exists()
    # return EnvBuilder(
    #     system_site_packages=system_site_packages, symlinks=True, with_pip=True, upgrade_deps=False
    # )
    return EnvBuilder(
        system_site_packages=False, symlinks=True, with_pip=True, upgrade_deps=False
    )


def get_root_pkg_path():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def create_base_command():
    return [
        "python",
        "-m",
        "lunarbase.orchestration.engine",
    ]


class OutputCatcher(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class PythonProcess(Process):
    CACHE_PATH: ClassVar[str] = "packages.pip"
    VENV_BUILDER: ClassVar[EnvBuilder] = create_venv_builder()

    venv_path: str = Field(default=...)
    command: List[str] = Field(default_factory=create_base_command)
    working_dir: Optional[str] = Field(default=None)
    venv_context: dict = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = False
        allow_mutation = True
        validate_assignment = True
        underscore_attrs_are_private = True

    @classmethod
    async def create(
        cls,
        venv_path: str,
        command: Optional[List[str]] = None,
        expected_packages: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        **additional_kwargs: Any,
    ):
        command = command or create_base_command()
        expected_packages = expected_packages or list()

        self = cls(
            venv_path=venv_path,
            command=command,
            working_dir=working_dir,
            **additional_kwargs,
        )

        if len(expected_packages) > 0:
            await self.install_packages(expected_packages, disable_cache=False)

        return self

    @validator("venv_path")
    @classmethod
    def validate_venv_path(cls, value):
        value = os.path.abspath(value)
        if not os.path.isdir(value) or not len(os.listdir(value)):
            cls.VENV_BUILDER.create(value)
        else:
            cls.VENV_BUILDER.ensure_directories(value)

        return value

    @root_validator(pre=False)
    @classmethod
    def update_fields(cls, values):
        if values.get("venv_path") is None:
            raise ValueError("Process cannot be run without a virtual environment.")

        if values.get("working_dir") is None:
            values["working_dir"] = values.get("venv_path")

        context = cls.VENV_BUILDER.ensure_directories(values.get("venv_path"))
        values["venv_context"] = vars(context)
        cmd = [context.env_exe, "-Im", "pip", "install", "--upgrade", "pip"]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        if not values.get("command", [""])[0].startswith(context.bin_path):
            values["command"][0] = os.path.join(
                context.bin_path, values.get("command", [""])[0]
            )

        env_values = dict()
        env_file = values.get("env_file")
        if env_file is not None:
            if not os.path.isfile(os.path.abspath(env_file)):
                warnings.warn(
                    f"Environment file {os.path.abspath(env_file)} not found! Environment will be incomplete."
                )
            try:
                env_values = dotenv_values(dotenv_path=os.path.abspath(env_file))
            except Exception as e:
                warnings.warn(
                    f"Failed to parse environment file {os.path.abspath(env_file)}! "
                    f"Details: {str(e)}. Environment will be incomplete."
                )
                env_values = dict()

        core_sys_paths = PythonProcess.get_core_info().get("locations", [])
        current_env = values.get("env", dict())
        current_env.update(**env_values)
        p_path = current_env.get("PYTHONPATH", "")
        p_path = ":".join(core_sys_paths + [p_path])
        if p_path.endswith(":"):
            p_path = p_path.rstrip(":")
        current_env["PYTHONPATH"] = p_path
        values["env"] = {**current_env}

        return values

    @staticmethod
    @lru_cache(maxsize=1024)
    def get_core_info():
        root_package_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        root_package_name = os.path.basename(root_package_path)

        from pip._vendor import pkg_resources

        try:
            _package = pkg_resources.working_set.by_key[root_package_name]
        except KeyError:
            return dict()
        requirement_names = {req.name for req in _package.requires()}

        locations = [_package.location]
        # Deal with .pth file for the parent package
        pth_path = f"{_package.location}/{root_package_name}.pth"
        if os.path.isfile(pth_path):
            with open(pth_path, "r") as p:
                locations.extend([line.rstrip() for line in p])

        return {
            "name": _package.project_name,
            "version": _package.version,
            "locations": locations,
            "requirements": requirement_names,
        }

    def check_installed(self, packages: List[str]):
        full_cache_path = os.path.join(self.venv_path, self.__class__.CACHE_PATH)
        try:
            new_packages = list(parse("\n".join(packages)))
        except Exception as e:
            raise ValueError(
                f"Failed to parse requirements {packages}. Details: {str(e)}"
            )

        try:
            with open(full_cache_path, "r") as reqs:
                existing_packages = {req.name: req for req in parse(reqs)}
        except FileNotFoundError:
            existing_packages = dict()
        except Exception as e:
            raise ValueError(
                f"Failed to parse cached requirements from {full_cache_path}. Details: {str(e)}"
            )

        frozen_reqs = PythonProcess.get_core_info().get("requirements", set())
        to_install = set()
        for req in new_packages:
            if req.name in frozen_reqs:
                warnings.warn(
                    f"Installation of {req.name} "
                    f"is currently not allow due to potential clashes with core functionalities."
                )
                continue

            if req.name in existing_packages and len(req.specs or []) == 0:
                continue
            elif (
                req.name in existing_packages
                and req.line.strip() == existing_packages[req.name].line.strip()
            ):
                continue

            to_install.add(req.line.strip())
            existing_packages[req.name] = req

        if len(to_install) > 0:
            existing_packages = [req.line.strip() for req in existing_packages.values()]
            with open(full_cache_path, "w") as reqs:
                for spec in existing_packages:
                    reqs.write(spec)
                    reqs.write("\n")
        return list(to_install)

    async def install_packages(self, packages: List[str], disable_cache: bool = False):
        if not disable_cache:
            packages = self.check_installed(packages)

        if len(packages) == 0:
            return

        # _use_threaded_child_watcher()

        # Open a subprocess to execute the flow run
        self.logger.info(f"Setting up package installation...")
        working_dir_ctx = contextlib.nullcontext(self.working_dir)
        with working_dir_ctx as working_dir:
            cmd = [
                self.venv_context["env_exe"],
                "-m",
                "pip",
                "install",
                "--require-virtualenv",
                "--isolated",
                "--timeout=180",
                "--disable-pip-version-check",
                "--no-input",
            ]
            cmd = cmd + packages
            self.logger.debug(f"Installing packages {packages} ...")

            kwargs: Dict[str, object] = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

            process = await run_process(
                cmd,
                stream_output=self.stream_output,
                task_status=None,
                task_status_handler=None,
                cwd=working_dir,
                **kwargs,
            )

        if process.returncode:
            help_message = None
            if process.returncode == -9:
                help_message = (
                    "This indicates that the process exited due to a SIGKILL signal. "
                    "Typically, this is either caused by manual cancellation or "
                    "high memory usage causing the operating system to "
                    "terminate the process."
                )
            if process.returncode == -15:
                help_message = (
                    "This indicates that the process exited due to a SIGTERM signal. "
                    "Typically, this is caused by manual cancellation."
                )
            elif process.returncode == 247:
                help_message = (
                    "This indicates that the process was terminated due to high "
                    "memory usage."
                )
            elif (
                # "Ctrl-C exit code on Win
                sys.platform == "win32"
                and process.returncode == 0xC000013A
            ):
                help_message = (
                    "Process was terminated due to a Ctrl+C or Ctrl+Break signal. "
                    "Typically, this is caused by manual cancellation."
                )

            self.logger.error(
                f"Package installation process exited with status code: {process.returncode}"
                + (f"; {help_message}" if help_message else "")
            )
        else:
            self.logger.info(f"Packages {packages} installed successfully.")
