# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import random

import tempfile

import contextlib
import os
import subprocess
import sys
import warnings
from functools import lru_cache
from io import StringIO
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional
from venv import EnvBuilder

from dotenv import dotenv_values
from prefect.utilities.processutils import run_process

# This is because Prefect's Infrastructure is still using Pydantic V1
from pydantic.v1 import Field, root_validator, validator, BaseModel
from requirements.parser import parse

from lunarbase.registry import CORE_COMPONENT_PATH

def create_venv_builder():
    # need system_site_packages=True inside docker
    system_site_packages = Path("/app/in_docker").exists()
    return EnvBuilder(
        system_site_packages=system_site_packages,
        symlinks=True,
        with_pip=True,
        upgrade_deps=False,
    )
    # return EnvBuilder(
    #     system_site_packages=False, symlinks=True, with_pip=True, upgrade_deps=False
    # )

def get_root_pkg_path():
    return str(Path(__file__).parent.parent.parent.parent)


def create_base_command():
    return [
        "python",
        "-m",
        "lunarbase.orchestration.engine",
    ]

class OutputCatcher(list):
    def __enter__(self):
        self._stdout = sys.stdout
        self._fd = self._stdout.fileno()
        self._old_fd = os.dup(self._fd)
        self._pipe_out, self._pipe_in = os.pipe()
        os.dup2(self._pipe_in, self._fd)
        self._stringio = StringIO()
        sys.stdout = self._stringio
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout
        os.dup2(self._old_fd, self._fd)
        os.close(self._old_fd)
        os.close(self._pipe_in)
        output = os.read(self._pipe_out, 1000000).decode()
        os.close(self._pipe_out)
        self.extend(self._stringio.getvalue().splitlines())
        self.extend(output.splitlines())
        del self._stringio


class PythonProcess:
    CACHE_PATH: ClassVar[str] = "packages.pip"
    VENV_BUILDER: ClassVar[EnvBuilder] = create_venv_builder()

    command: List[str] = Field(default_factory=create_base_command)
    working_dir: Optional[str] = Field(default=None)

    def __init__(
        self,
        venv_path: str,
        command: Optional[List[str]] = None,
        expected_packages: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        env_file: Optional[str] = None,
        **kwargs: Any,
    ):
        self.venv_path = Path(venv_path)
        self.command = command or create_base_command()
        self.working_dir = working_dir or str(self.venv_path)
        self.env_file = env_file
        self.env: Dict[str, str] = {}
        self.venv_context: Dict[str, Any] = {}
        self.logger = kwargs.get("logger", __import__("logging").getLogger(__name__))
        self.stream_output = kwargs.get("stream_output", False)


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
        self._setup_venv()

        if len(expected_packages) > 0:
            await self.install_packages(expected_packages, disable_cache=False)

        return self

    @validator("venv_path")
    @classmethod
    def validate_venv_path(cls, value):
        value = Path(value)
        if not value.is_dir() or not len(list(value.iterdir())):
            cls.VENV_BUILDER.create(str(value))
        else:
            cls.VENV_BUILDER.ensure_directories(str(value))

        return value

    def _setup_venv(self):
        # create venv if missing
        if not self.venv_path.is_dir() or not any(self.venv_path.iterdir()):
            PythonProcess.VENV_BUILDER.create(str(self.venv_path))
        else:
            PythonProcess.VENV_BUILDER.ensure_directories(str(self.venv_path))

        # get the venv context
        context = PythonProcess.VENV_BUILDER.ensure_directories(str(self.venv_path))

        if sys.platform == 'win32':
            libpath = os.path.join(context.env_dir, 'Lib', 'site-packages')
        else:
            libpath = os.path.join(context.env_dir, 'lib',
                                   'python%d.%d' % sys.version_info[:2],
                                   'site-packages')
        context.libpath = libpath

        self.venv_context = vars(context)

        # upgrade pip
        subprocess.check_output(
            [context.env_exe, "-Im", "pip", "install", "--upgrade", "pip"],
            stderr=subprocess.STDOUT,
        )

        # rewrite command[0] to use the venv python
        cmd0 = Path(context.bin_path, Path(self.command[0]).name)
        self.command[0] = str(cmd0)

        # load dotenv if provided
        env_values = {}
        if self.env_file:
            if not Path(self.env_file).is_file():
                warnings.warn(f"Environment file {self.env_file} not found!")
            env_values = dotenv_values(dotenv_path=self.env_file) or {}

        # build PYTHONPATH
        core_info = PythonProcess.get_core_info()
        core_paths = core_info.get("locations", [])
        existing = dict(os.environ)
        existing.update(env_values)
        pythonpath = existing.get("PYTHONPATH", "")
        pythonpath_entries = core_paths + [context.libpath]
        if pythonpath:
            pythonpath_entries.append(pythonpath)
        existing["PYTHONPATH"] = ":".join(pythonpath_entries)
        self.env = existing

    @root_validator(pre=False)
    @classmethod
    def update_fields(cls, values):
        if values.get("venv_path") is None:
            raise ValueError("Process cannot be run without a virtual environment.")

        if values.get("working_dir") is None:
            values["working_dir"] = values.get("venv_path")

        context = cls.VENV_BUILDER.ensure_directories(values.get("venv_path"))

        if sys.platform == 'win32':
            libpath = os.path.join(context.env_dir, 'Lib', 'site-packages')
        else:
            libpath = os.path.join(context.env_dir, 'lib',
                                   'python%d.%d' % sys.version_info[:2],
                                   'site-packages')
        context.libpath = libpath

        values["venv_context"] = vars(context)
        cmd = [context.env_exe, "-Im", "pip", "install", "--upgrade", "pip"]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        if not values.get("command", [""])[0].startswith(context.bin_path):
            values["command"][0] = str(
                Path(context.bin_path, values.get("command", [""])[0])
            )

        env_values = dict()
        env_file = values.get("env_file")
        if env_file is not None:
            if not Path(env_file).is_file():
                warnings.warn(
                    f"Environment file {env_file} not found! Environment will be incomplete."
                )
            try:
                env_values = dotenv_values(dotenv_path=env_file)
            except Exception as e:
                warnings.warn(
                    f"Failed to parse environment file {env_file}! "
                    f"Details: {str(e)}. Environment will be incomplete."
                )
                env_values = dict()

        core_sys_paths = PythonProcess.get_core_info().get("locations", [])
        current_env = values.get("env", dict())
        current_env.update(**env_values)
        p_path = current_env.get("PYTHONPATH", "")
        p_path = ":".join(core_sys_paths + [context.libpath] + [p_path])
        if p_path.endswith(":"):
            p_path = p_path.rstrip(":")
        current_env["PYTHONPATH"] = p_path
        values["env"] = {**current_env}

        return values

    @staticmethod
    @lru_cache(maxsize=1024)
    def get_core_info():
        root_package_path = get_root_pkg_path()
        root_package_name = Path(root_package_path).name

        from pip._vendor import pkg_resources

        try:
            _package = pkg_resources.working_set.by_key[root_package_name]
        except KeyError:
            return dict()
        requirement_names = {req.name for req in _package.requires()}

        locations = [_package.location, CORE_COMPONENT_PATH]
        # Deal with .pth file for the parent package
        pth_path = Path(_package.location, f"{root_package_name}.pth")
        if pth_path.is_file():
            with open(str(pth_path), "r") as p:
                locations.extend([line.rstrip() for line in p])

        return {
            "name": _package.project_name,
            "version": _package.version,
            "locations": locations,
            "requirements": requirement_names,
        }

    def check_installed(self, packages: List[str]):
        full_cache_path = str(Path(self.venv_path, self.__class__.CACHE_PATH))
        try:
            new_packages = list(parse(os.linesep.join(packages)))
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
                    reqs.write(os.linesep)
        return list(to_install)

    async def run(self):
        display_name = self._generate_lunar_name()
        self.logger.info(f"Opening process{display_name}...")

        working_dir_ctx = (
            tempfile.TemporaryDirectory(suffix="prefect")
            if not self.working_dir
            else contextlib.nullcontext(self.working_dir)
        )
        with working_dir_ctx as working_dir:
            self.logger.debug(
                f"Process{display_name} running command: {' '.join(self.command)} in"
                f" {working_dir}"
            )
            kwargs: Dict[str, object] = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            process = await run_process(
                self.command,
                stream_output=self.stream_output,
                task_status=None,
                task_status_handler=None,
                env=self._get_environment_variables(),
                cwd=working_dir,
                **kwargs,
            )
            display_name = display_name or f" {process.pid}"
            # exit code indicating that the process was terminated by Ctrl+C or Ctrl+Break
            STATUS_CONTROL_C_EXIT = 0xC000013A

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
                        sys.platform == "win32" and process.returncode == STATUS_CONTROL_C_EXIT
                ):
                    help_message = (
                        f"Process was terminated due to a Ctrl+C or Ctrl+Break signal. "
                        f"Typically, this is caused by manual cancellation."
                    )

                self.logger.error(
                    f"Process{display_name} exited with status code: {process.returncode}"
                    + (f"; {help_message}" if help_message else "")
                )
            else:
                self.logger.info(f"Process{display_name} exited cleanly.")
            return process


    async def install_packages(self, packages: List[str], disable_cache: bool = False):
        if not disable_cache:
            packages = self.check_installed(packages)
        if len(packages) == 0:
            return

        # _use_threaded_child_watcher()

        # Open a subprocess to execute the flow run
        self.logger.info(f"Setting up package installation...")
        working_dir_ctx = contextlib.nullcontext(self.working_dir)
        packages_set = set(packages) - sys.stdlib_module_names
        packages = list(packages_set)
        with working_dir_ctx as working_dir:
            cmd = [
                self.venv_context["env_exe"],
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
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

    def _generate_lunar_name(self):
        adjectives = {
            "lunar", "stellar", "cosmic", "galactic", "orbital", "celestial", "silent",
            "solar", "radiant", "frozen", "void", "infinite", "tidal", "nebular", "cratered",
            "distant", "dark", "bright", "eclipsed", "ghostly"
        }
        nouns = {
            "ranger", "explorer", "voyager", "pioneer", "comet", "module", "capsule", "lander",
            "hopper", "crater", "satellite", "station", "rover", "observer", "mission", "engine",
            "telescope", "drifter", "base", "pathfinder"
        }
        adjective = random.choice(list(adjectives))
        noun = random.choice(list(nouns))
        return f"{adjective} {noun}"

    def _get_environment_variables(self, include_os_environ: bool = True):
        os_environ = os.environ if include_os_environ else {}
        env = {**os_environ, **self.env}
        return {key: value for key, value in env.items() if value is not None}