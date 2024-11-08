# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import pathlib
import sys
from functools import partial

from prefect.exceptions import ObjectNotFound
from prefect.server.schemas.responses import SetStateStatus
from rich import print as rprint
from dotenv import load_dotenv
from prefect.cli._types import PrefectTyper as AsyncTyper
from prefect.utilities.processutils import run_process, setup_signal_handlers_server
from prefect import get_client
from prefect.client.schemas import StateType
from prefect.client.schemas.filters import (
    FlowRunFilter,
    FlowRunFilterState,
    FlowRunFilterStateType,
    FlowRunFilterName,
)
from prefect.client.schemas.sorting import FlowRunSort
from prefect.states import Cancelling

from typing import Annotated, Optional
import lunarbase
import anyio
import typer
from lunarbase.config import LunarConfig
from lunarbase.controllers.component_controller import (
    ComponentController,
)
from lunarbase.controllers.workflow_controller import WorkflowController
from lunarbase.modeling.data_models import (
    WorkflowModel,
    ComponentModel,
)
from lunarbase.persistence import PersistenceLayer
from lunarbase.registry import LunarRegistry
from lunarbase.utils import setup_logger
from lunarbase import LUNAR_CONTEXT

from copy import deepcopy

app = AsyncTyper(
    name="Lunarbase server app",
    help="Start a Lunarbase server instance",
)
workflow = AsyncTyper(
    name="Lunarbase workflow subcommand", help="Run commands on workflows."
)
component = AsyncTyper(
    name="Lunarbase component subcommand", help="Run commands on components."
)

app.add_typer(workflow, name="workflow")
app.add_typer(component, name="component")

app_context = deepcopy(LUNAR_CONTEXT)
app_context.workflow_controller = WorkflowController(config=LUNAR_CONTEXT.lunar_config)
app_context.component_controller = ComponentController(
    config=LUNAR_CONTEXT.lunar_config
)
app_context.persistence_layer = PersistenceLayer(config=LUNAR_CONTEXT.lunar_config)

logger = setup_logger("lunarbase-cli")


@app.callback()
def run():
    """
    Lunarbase CLI 🚀
    """


@app.command(name="start", short_help="Start the lunarbase server.")
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
        logger.info("Lunarbase server starting ...")

        app_context.persistence_layer.init_local_storage()

        await LUNAR_CONTEXT.lunar_registry.register()

        env_file = env_file or LunarConfig.DEFAULT_ENV
        server_env = dict()
        if pathlib.Path(env_file).is_file():

        if pathlib.Path('/app/in_docker').is_file():
            env_file = GLOBAL_CONFIG.DOCKER_ENV
        if pathlib.Path(env_file).is_file():
            load_dotenv(env_file)
            server_env = os.environ.copy()

        server_env["LUNARBASE_ADDRESS"] = str(server_env.get("LUNARBASE_ADDRESS")) or str(host)
        server_env["LUNARBASE_PORT"] = str(server_env.get("LUNARBASE_PORT")) or str(port)

        server_process_id = await tg.start(
            partial(
                run_process,
                command=[
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "lunarbase.api:app",
                    "--app-dir",
                    f'"{pathlib.Path(lunarbase.__file__).parent.parent}"',
                    "--host",
                    str(server_env["LUNARBASE_ADDRESS"]),
                    "--port",
                    str(server_env["LUNARBASE_PORT"]),
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

    app.console.print("Lunarcore server stopped!")
    logger.info("Lunarcore server stopped!")


@workflow.command(
    name="run",
    short_help="Initiate the run of a workflow.",
)
async def run_workflow(
    user: Annotated[str, typer.Option(help="User id to run as.")],
    location: Annotated[
        str,
        typer.Argument(help="A path to a workflow or component to run as a JSON file."),
    ],
    show: Annotated[bool, typer.Option(help="Print the output to STDOUT")] = False,
):
    # if len(LUNAR_CONTEXT.lunar_registry.components) == 0:
    #     await LUNAR_CONTEXT.lunar_registry.load_components()

    user = user or app_context.workflow_controller.config.DEFAULT_USER_PROFILE
    with open(location, "r") as file:
        obj = json.load(file)
    workflow = WorkflowModel.model_validate(obj)
    workflow_result = await app_context.workflow_controller.run(
        workflow=workflow, user_id=user
    )
    if show:
        rprint(workflow_result)
    return json.dumps(workflow_result)


@component.command(
    name="run",
    short_help="Initiate the run of a component as a workflow.",
)
async def run_component(
    user: Annotated[str, typer.Option(help="User id to run as.")],
    location: Annotated[
        str,
        typer.Argument(help="A path to a workflow or component to run as a JSON file."),
    ],
    show: Annotated[bool, typer.Option(help="Print the output to STDOUT")] = False,
):
    # if len(LUNAR_CONTEXT.lunar_registry.components) == 0:
    #     await LUNAR_CONTEXT.lunar_registry.load_components()

    user = user or app_context.component_controller.config.DEFAULT_USER_PROFILE
    with open(location, "r") as file:
        obj = json.load(file)
    component = ComponentModel.model_validate(obj)
    component_result = await app_context.component_controller.run(
        component=component, user_id=user
    )
    if show:
        rprint(component_result)
    return json.dumps(component_result)


@component.command(
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
    # if len(LUNAR_CONTEXT.lunar_registry.components) == 0:
    #     await LUNAR_CONTEXT.lunar_registry.load_components()

    location = pathlib.Path(location)
    if location.is_file():
        with open(location.as_posix(), "r") as f:
            component_obj = json.load(f)
        component = ComponentModel.model_validate(component_obj)
    elif location.is_dir():
        component = LunarRegistry.generate_component_model(location.as_posix())
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


@workflow.command(
    name="runtime",
    short_help="List currently running workflows",
)
async def runtime(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Filter by this workflow"),
    ] = None,
    limit: Annotated[
        int,
        typer.Argument(help="Filter by this workflow"),
    ] = None,
):
    from prefect import get_client
    from prefect.client.schemas import StateType
    from prefect.client.schemas.filters import (
        FlowRunFilter,
        FlowFilterId,
        FlowFilter,
        FlowRunFilterState,
        FlowRunFilterStateType,
    )

    client = get_client()
    async with client:
        flow_run_data = await client.read_flow_runs(
            flow_filter=(
                FlowFilter(id=FlowFilterId(any_=[workflow_id]))
                if workflow_id is not None
                else None
            ),
            flow_run_filter=FlowRunFilter(
                state=FlowRunFilterState(
                    type=FlowRunFilterStateType(
                        any_=[
                            StateType.RUNNING,
                            StateType.PAUSED,
                            StateType.PENDING,
                            StateType.SCHEDULED,
                            StateType.CANCELLING,
                        ]
                    )
                )
            ),
            limit=limit,
        )

        rprint([fd.dict() for fd in flow_run_data or []])


@workflow.command(
    name="cancel",
    short_help="Cancel a running workflow!",
)
async def cancel_workflow(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Workflow ID"),
    ]
):
    client = get_client()
    async with client:
        flow_run_data = await client.read_flow_runs(
            # flow_filter=FlowFilter(id=FlowFilterId(any_=[workflow_id])),
            flow_run_filter=FlowRunFilter(
                name=FlowRunFilterName(any_=[workflow_id]),
                state=FlowRunFilterState(
                    type=FlowRunFilterStateType(
                        any_=[
                            StateType.RUNNING,
                            StateType.PAUSED,
                            StateType.PENDING,
                            StateType.SCHEDULED,
                        ]
                    )
                ),
            ),
            sort=FlowRunSort.START_TIME_DESC,
            limit=1,
        )

        current_runs = [fd.dict() for fd in flow_run_data or []]
        if not len(current_runs):
            app.console.print(
                f"No runs found for workflow {workflow_id}. Nothing to cancel."
            )
            return

        app.console.print(
            f"Cancelling workflow {workflow_id} in run {current_runs[0]['id']} ..."
        )
        cancelling_state = Cancelling(message="Cancelling at admin's request!")
        try:
            result = await client.set_flow_run_state(
                flow_run_id=current_runs[0]["id"], state=cancelling_state
            )
        except ObjectNotFound:
            app.console.print(f"Flow run '{id}' not found!")

        if result.status == SetStateStatus.ABORT:
            app.console.print(
                f"Flow run '{id}' was unable to be cancelled. Reason:"
                f" '{result.details.reason}'"
            )
            return

        app.console.print(
            f"Workflow {workflow_id} in run {current_runs[0]['id']} "
            f"was successfully scheduled for cancellation with status: {result.status}"
        )
