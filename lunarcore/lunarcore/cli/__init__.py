# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import pathlib
import sys
from functools import partial

from rich import print as rprint
from dotenv import load_dotenv
from prefect.cli._types import PrefectTyper as AsyncTyper
from prefect.utilities.processutils import run_process, setup_signal_handlers_server
from typing import Annotated, Optional

import anyio
import typer
from types import SimpleNamespace
import lunarcore
from lunarcore import GLOBAL_CONFIG
from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.controllers.component_controller import ComponentController
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import (
    WorkflowModel,
    ComponentModel,
)
from lunarcore.core.registry import ComponentRegistry
from lunarcore.utils import setup_logger

app = AsyncTyper(
    name="Lunarcore server app",
    help="Start a Lunarcore server instance",
)
app_context = SimpleNamespace()
app_context.workflow_controller = WorkflowController(config=GLOBAL_CONFIG)
app_context.component_controller = ComponentController(config=GLOBAL_CONFIG)

logger = setup_logger("lunarcore-cli")


@app.callback()
def run():
    """
    Lunarcore CLI 🚀
    """


@app.command(name="start", short_help="Start the lunarcore server.")
async def start(
    host: Optional[str] = typer.Option(
        default="127.0.0.1", help="The IP address or hostname to listen on."
    ),
    port: Optional[int] = typer.Option(default="8088", help="The port to listen on."),
    env_file: Optional[str] = typer.Option(
        default=None, help="The environment to use."
    ),
):
    async with anyio.create_task_group() as tg:
        # app.console.print("Lunarcore server starting ...")
        logger.info("Lunarcore server starting ...")

        await COMPONENT_REGISTRY.register(fetch=True)

        env_file = (
            env_file or f"{str(pathlib.Path(lunarcore.__file__).parent.parent.parent)}/.env"
        )
        if os.path.isfile(env_file):
            load_dotenv(env_file)
            server_env = os.environ.copy()
        else:
            server_env = None

        server_env["LUNARCORE_ADDRESS"] = server_env.get("LUNARCORE_ADDRESS") or host
        server_env["LUNARCORE_PORT"] = server_env.get("LUNARCORE_PORT") or port

        server_process_id = await tg.start(
            partial(
                run_process,
                command=[
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "lunarcore.api:app",
                    "--app-dir",
                    f'"{pathlib.Path(lunarcore.__file__).parent.parent}"',
                    "--host",
                    str(server_env["LUNARCORE_ADDRESS"]),
                    "--port",
                    str(server_env["LUNARCORE_PORT"]),
                ],
                env=server_env,
                stream_output=True,
            )
        )
        # app.console.print("Lunarcore server started successfully!")
        logger.info("Lunarcore server started successfully!")
        setup_signal_handlers_server(
            server_process_id, "the Lunarcore server", app.console.print
        )

    # app.console.print("Lunarcore server stopped!")
    logger.info("Lunarcore server stopped!")


@app.command(
    name="run",
    short_help="Initiate the run of a component or an entire workflow.",
)
async def run(
    user: Annotated[str, typer.Option(help="User id to run as.")],
    location: Annotated[
        str,
        typer.Argument(help="A path to a workflow or component to run as a JSON file."),
    ],
    show: Annotated[bool, typer.Option(help="Print the output to STDOUT")] = False,
):
    if len(COMPONENT_REGISTRY.components) == 0:
        await COMPONENT_REGISTRY.register(fetch=False)

    with open(location, "r") as file:
        obj = json.load(file)
    if "components" in obj:
        workflow = WorkflowModel.model_validate(obj)
        workflow_result = await app_context.workflow_controller.run(
            workflow=workflow, user_id=user
        )
        if show:
            rprint(workflow_result)
        return json.dumps(workflow_result)

    component = ComponentModel.model_validate(obj)
    component_result = await app_context.component_controller.run(component=component)
    if show:
        rprint(component_result)
    return json.dumps(component_result)


@app.command(
    name="exemplify",
    short_help="Generate an example workflow from a component given as a JSON or code.",
)
async def exemplify(
    location: Annotated[
        str,
        typer.Argument(
            help="A path to a component's JSON file or Python package directory."
        ),
    ],
    save: Annotated[
        str,
        typer.Option(help="A path to save the output as a workflow in JSON format."),
    ] = None,
    show: Annotated[bool, typer.Option(help="Print the result to STDOUT")] = False,
):
    if len(COMPONENT_REGISTRY.components) == 0:
        await COMPONENT_REGISTRY.register(fetch=False)

    location = pathlib.Path(location)
    if location.is_file():
        with open(location.as_posix(), "r") as f:
            component_obj = json.load(f)
        component = ComponentModel.model_validate(component_obj)
    elif location.is_dir():
        component = ComponentRegistry.generate_component_model(location.as_posix())
    else:
        raise FileNotFoundError(f"{location.as_posix()} not found!")

    workflow = WorkflowModel(
        user_id="",
        name=f"{component.name} component example",
        description=f"A one-component workflow illustrating the use of {component.name} component.",
        components=[component],
    )
    workflow_dict = workflow.model_dump()
    if save is not None:
        with open(save, "w") as f:
            json.dump(workflow_dict, f, indent=4)

    if show:
        rprint(workflow_dict)
