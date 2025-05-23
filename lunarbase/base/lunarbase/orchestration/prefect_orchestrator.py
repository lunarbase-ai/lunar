from prefect.futures import PrefectFuture
from typing import Dict, List, Any, Callable, Union
from datetime import timedelta

from prefect.task_runners import ConcurrentTaskRunner
from prefect import Flow, get_client, task
from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId

from lunarbase.config import LunarConfig
from lunarbase.components.component_wrapper import ComponentWrapper
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel
from lunarbase.orchestration.task_promise import TaskPromise
from lunarbase.orchestration.utils import update_inputs
from lunarbase.orchestration.callbacks import cancelled_flow_handler


def generate_prefect_cache_key(context, arguments):
    component = arguments.get("component_wrapper").component_model
    _key = f"{context.task.task_key}-{context.task.fn.__code__.co_code.hex()[:15]}-{component.label}-{'_'.join([str(hash(c_input)) for c_input in component.inputs])}"
    return _key

@task(cache_key_fn=generate_prefect_cache_key, cache_expiration=timedelta(minutes=10))
def run_prefect_task(
        component_wrapper: ComponentWrapper,
):
    try:
        result = component_wrapper.run_in_workflow()
    except Exception as e:
        raise ComponentError(str(e))

    return result

@task(refresh_cache=True, persist_result=False)
def stream_prefect_task(
        component: ComponentWrapper,
        promises: Dict,
):
    streams = []
    links = []
    for link, _promise in promises.items():
        link = link.split(".", 1)
        link_key, link_template = link[0], None
        if len(link_key) > 1:
            link_template = link[1]

        promise_results = _promise.run()
        links.append((link_key, link_template))
        streams.append(promise_results)

    task_result = None
    for results in zip(*streams):
        current_model = component.component_model
        for (link_key, link_template), promised_model in zip(links, results):
            current_model = update_inputs(
                current_task=current_model,
                upstream_task=promised_model,
                upstream_label=promised_model.label,
                input_key=link_key,
                template_key=link_template,
            )
        component.component_model = current_model
        try:
            task_result = component.run_in_workflow()
        except Exception as e:
            raise ComponentError(str(e))

    return task_result


@task()
def assign_output_task(model, output):
    model.output = output
    return model

class PrefectOrchestrator:
    def __init__(
        self,
        config: LunarConfig
    ):
        self.config = config

    def run_task(self, component_wrapper: ComponentWrapper, upstream: List[ dict[Any, ComponentError | TaskPromise]]):
        return run_prefect_task.with_options(
            name=component_wrapper.component_model.label,
            refresh_cache=component_wrapper.disable_cache,
            persist_result=True,
        ).submit(
            component_wrapper=component_wrapper,
            wait_for=upstream,
        )

    def stream_task(
            self,
            component_wrapper: ComponentWrapper,
            promises:  dict[str | None, dict],
            next_task: str,
            upstream: List[dict[Any, ComponentError | TaskPromise]],
    ):
        return stream_prefect_task.with_options(
            name=f"Task {component_wrapper.component_model.name}"
        ).submit(
            component_instance=component_wrapper,
            promises=promises[next_task],
            wait_for=upstream,
        )

    def assign_output(self, component: ComponentModel, output: Any):
        return assign_output_task.submit(
            model=component, output=output
        )

    def map_workflow_to_prefect_flow(
            self,
            flow_function: Callable,
            workflow: WorkflowModel,
    ):
        return Flow(
            fn=flow_function,
            name=workflow.name,
            flow_run_name=workflow.id,
            description=workflow.description,
            version=workflow.version,
            timeout_seconds=workflow.timeout,
            task_runner=ConcurrentTaskRunner(),
            validate_parameters=False,
            retries=None,
            on_cancellation=[cancelled_flow_handler],
        )

    def run_step(self, step: Union[PrefectFuture, ComponentError]):
        if isinstance(step, ComponentError):
            return step
        try:
            step_result = step.result(raise_on_failure=True)
        except Exception as e:
            e = ComponentError(str(e))
            step_result = e

        return step_result

    async def get_task_runs(self, flow_run_id:str):
        with get_client() as client:
            current_task_runs = await client.read_task_runs(
                flow_run_filter=FlowRunFilter(id=FlowRunFilterId(any_=[flow_run_id])),
            )
        return current_task_runs
