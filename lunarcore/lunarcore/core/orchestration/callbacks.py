import json

from prefect import Flow
from prefect.client.schemas import FlowRun
from prefect.server.schemas.states import State

from lunarcore.core.data_models import WorkflowModel, WorkflowRuntimeModel


def cancelled_flow_handler(flow, flow_run, state) -> None:
    pass


def crashed_flow_handler(flow, flow_run, state) -> None:
    pass


def failed_flow_handler(flow, flow_run, state) -> None:
    pass


def completed_flow_handler(flow, flow_run, state) -> None:
    pass


async def running_flow_handler(flow, flow_run, state) -> None:
    workflow_path = flow_run.parameters['flow_path']
    with open(workflow_path, "r") as w:
        workflow = WorkflowModel(**json.load(w))
    runtime = WorkflowRuntimeModel(
        workflow_id=workflow.id,
        state=state.type,
        elapsed=0.0
    )
    workflow.runtime = runtime
    with open(workflow_path, 'w') as f:
        f.write(json.dumps(workflow.dict(), indent=2))
        # json.dump(workflow.dict(), f)
