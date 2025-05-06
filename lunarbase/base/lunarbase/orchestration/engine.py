# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import time
import asyncio
import argparse
import json
from collections import deque
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

from lunarbase.components.component_wrapper import ComponentWrapper
from lunarbase.components.subworkflow import Subworkflow
from lunarbase.orchestration.callbacks import cancelled_flow_handler
from lunarbase.orchestration.process import (
    OutputCatcher,
    PythonProcess,
    create_base_command,
)
from lunarbase.orchestration.task_promise import TaskPromise
from lunarbase.utils import setup_logger
from lunarcore.component.data_types import DataType
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.component_encoder import ComponentEncoder
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel
from prefect import Flow, get_client, task
from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId
from prefect.futures import PrefectFuture
from prefect.task_runners import ConcurrentTaskRunner
from lunarbase.registry import LunarRegistry

from lunarbase.domains.workflow.event_dispatcher import EventDispatcher

MAX_RESULT_DICT_LEN = 10
MAX_RESULT_DICT_DEPTH = 2

RUN_OUTPUT_START = "<COMPONENT OUTPUT START>"
RUN_OUTPUT_END = "<COMPONENT OUTPUT END>"

WORKFLOW_OUTPUT_START = "<WORKFLOW OUTPUT START>"
WORKFLOW_OUTPUT_END = "<WORKFLOW OUTPUT END>"

logger = setup_logger("orchestration-engine")


def generate_prefect_cache_key(context, arguments):
    component = arguments.get("component_wrapper").component_model
    _key = f"{context.task.task_key}-{context.task.fn.__code__.co_code.hex()[:15]}-{component.label}-{'_'.join([str(hash(c_input)) for c_input in component.inputs])}"
    return _key

#TODO: change to 10 minutes
@task(cache_key_fn=generate_prefect_cache_key, cache_expiration=timedelta(seconds=10))
def run_prefect_task(
    component_wrapper: ComponentWrapper,
):
    try:
        result = component_wrapper.run_in_workflow()
    except Exception as e:
        raise ComponentError(str(e))

    return result


async def gather_partial_flow_results(flow_run_id: str):
    with get_client() as client:
        current_task_runs = await client.read_task_runs(
            flow_run_filter=FlowRunFilter(id=FlowRunFilterId(any_=[flow_run_id])),
        )

    current_task_results = dict()
    for tr in current_task_runs or []:
        if tr.state.is_completed():
            _result = tr.state.result(raise_on_failure=False).get()
            current_task_results[_result.label] = _result
        else:
            _result = ComponentError(f"{tr.state.name}: {tr.state.message}!")
            current_task_results[tr.name] = _result
    return current_task_results


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

    result = None
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
            result = component.run_in_workflow()
        except Exception as e:
            raise ComponentError(str(e))

    return result


def update_inputs(
    current_task: ComponentModel,
    upstream_task: ComponentModel,
    upstream_label: str,
    input_key: str,
    template_key: Optional[str] = None,
):
    for i in range(len(current_task.inputs)):
        if current_task.inputs[i].key != input_key:
            continue

        if template_key is not None:
            template_key_factors = template_key.split(".", maxsplit=1)
            if len(template_key_factors) < 2:
                template_key = f"{input_key}.{template_key}"
            elif template_key_factors[0] != input_key:
                raise ValueError(
                    f"Something is wrong with the template variables. Expected parent variable {input_key}, got {template_key_factors[0]}!"
                )

            current_task.inputs[i].template_variables[
                template_key
            ] = upstream_task.output.value
        elif current_task.inputs[i].data_type == DataType.AGGREGATED:
            if not isinstance(current_task.inputs[i].value, dict):
                current_task.inputs[i].value = {}
            current_task.inputs[i].value[upstream_label] = upstream_task.output.value
        else:
            current_task.inputs[i].value = upstream_task.output.value

        break
    return current_task


def create_flow_dag(
    workflow: WorkflowModel,
    lunar_registry: LunarRegistry
):
    tasks = {comp.label: comp for comp in workflow.components}
    promises = {comp.label: dict() for comp in workflow.components}
    dag = workflow.get_dag()
    running_queue = deque(list(dag.nodes))
    real_tasks = dict()
    while len(running_queue) > 0:
        next_task = running_queue.popleft()
        upstream = []
        try:
            for dep in dag.predecessors(next_task):
                if not isinstance(real_tasks[dep], TaskPromise):
                    upstream.append(real_tasks[dep])
                else:
                    for _, data in dag[dep][next_task].items():
                        link_input_key, link_template_key = data.get(
                            "data", (None, None)
                        )
                        link_key = (
                            link_input_key
                            if link_template_key is None
                            else f"{link_input_key}.{link_template_key}"
                        )

                        # Only one STREAM per input allowed. Multiple streams would require zip
                        promises[next_task][link_key] = real_tasks[dep]

        except KeyError:
            running_queue.append(next_task)
            continue

        previously_failed = None
        for pred, _, (input_key, template_key) in dag.in_edges(next_task, data="data"):
            if isinstance(real_tasks[pred], TaskPromise):
                continue

            upstream_result = run_step(real_tasks[pred])
            if isinstance(upstream_result, ComponentError):
                previously_failed = upstream_result
                break

            tasks[next_task] = update_inputs(
                current_task=tasks[next_task],
                upstream_task=upstream_result,
                upstream_label=pred,
                input_key=input_key,
                template_key=template_key,
            )

        if previously_failed is not None:
            real_tasks[next_task] = ComponentError(
                "Run upstream components first or see their return errors for details!"
            )
            continue

        try:
            obj = ComponentWrapper(component=tasks[next_task], lunar_registry=lunar_registry)
        except ComponentError as e:
            real_tasks[next_task] = e
            logger.error(f"Error running {tasks[next_task].label}: {str(e)}", exc_info=True)
            continue
        if obj.component_model.class_name == Subworkflow.__name__:
            @task()
            def assign_output(model, output):
                model.output = output
                return model
            subworkflow = Subworkflow.subworkflow_validation(obj.component_model)
            _tasks = create_flow_dag(subworkflow, lunar_registry=lunar_registry)
            error = None
            for subsid, substate in _tasks.items():
                subresult = run_step(substate)

                if isinstance(subresult, ComponentError):
                    #Only show the first subworkflow error
                    if error is None:
                        error = subresult
                        real_tasks[next_task] = subresult
                    continue

                if subresult.is_terminal:
                    real_tasks[next_task] = assign_output.submit(
                        model=tasks[next_task], output=subresult.output
                    )
                    break
        elif len(promises[next_task]) > 0:
            real_tasks[next_task] = stream_prefect_task.with_options(
                name=f"Task {obj.component_model.name}"
            ).submit(
                component_instance=obj,
                promises=promises[next_task],
                wait_for=upstream,
            )
        else:
            if obj.component_model.output.data_type == DataType.STREAM:
                try:
                    next(dag.successors(next_task))
                    real_tasks[next_task] = TaskPromise(obj)
                    continue
                except StopIteration:
                    pass
            real_tasks[next_task] = run_prefect_task.with_options(
                name=obj.component_model.label,
                refresh_cache=obj.disable_cache,
                persist_result=True,
            ).submit(
                component_wrapper=obj,
                wait_for=upstream,
            )
    return real_tasks


def run_step(step: Union[PrefectFuture, ComponentError]):
    if isinstance(step, ComponentError):
        return step
    try:
        result = step.result(raise_on_failure=True)
    except Exception as e:
        e = ComponentError(str(e))
        result = e

    return result


def create_flow(workflow_path: str, lunar_registry: LunarRegistry):
    with open(workflow_path, "r") as w:
        workflow = json.load(w)
    workflow = WorkflowModel.model_validate(workflow)
    tasks = create_flow_dag(workflow, lunar_registry=lunar_registry)
    states_id = list(tasks.keys())
    results = {}
    for sid in states_id:
        if isinstance(tasks[sid], TaskPromise):
            results[sid] = tasks[sid].component.component_model
            continue
        results[sid] = run_step(tasks[sid])
        print(f"{RUN_OUTPUT_START}", flush=True)
        json_out = json.dumps(results[sid], cls=ComponentEncoder)
        print(f"{json_out}", flush=True)
        print(f"{RUN_OUTPUT_END}", flush=True)
    return results


def create_task_flow(
    component_path: str,
    lunar_registry: LunarRegistry
):
    with open(component_path, "r") as w:
        component = json.load(w)
    component = ComponentModel.model_validate(component)

    try:
        obj = ComponentWrapper(component, lunar_registry=lunar_registry)
        if obj.component_model.class_name == Subworkflow.__name__:
            subworkflow = Subworkflow.subworkflow_validation(obj.component_model)
            result = None
            flow_results = create_flow(subworkflow, lunar_registry=lunar_registry)
            for _, subresult in flow_results.items():
                if subresult.is_terminal:
                    component.output = subresult.output
                    result = component
                    break
        else:
            prefect_task = run_prefect_task.with_options(
                name=obj.component_model.label,
                refresh_cache=obj.disable_cache,
            ).submit(
                component_wrapper=obj,
                wait_for=None,
            )
            result = run_step(prefect_task)
    except ComponentError as e:
        logger.error(f"Error running {component.label}: {str(e)}.", exc_info=True)
        result = e

    return {component.label: result}


def component_to_prefect_flow(
    component_path: str,
    lunar_registry: LunarRegistry
) -> Flow:
    with open(component_path, "r") as w:
        component = json.load(w)

    component = ComponentModel.model_validate(component)

    def flow_fn(*args, **kwargs):
        return create_task_flow(*args, lunar_registry=lunar_registry, **kwargs)

    return Flow(
        fn=flow_fn,
        name=component.name,
        flow_run_name=component.id,
        description=component.description,
        version=component.version,
        timeout_seconds=component.timeout,
        task_runner=ConcurrentTaskRunner(),
        validate_parameters=False,
    )


def workflow_to_prefect_flow(
    workflow_path: str,
    lunar_registry: LunarRegistry
):
    with open(workflow_path, "r") as w:
        workflow = json.load(w)

    workflow = WorkflowModel.model_validate(workflow)
    def flow_fn(*args, **kwargs):
        return create_flow(*args, lunar_registry=lunar_registry, **kwargs)
    return Flow(
        fn=flow_fn,
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


def gather_component_dependencies(components: List[ComponentModel], lunar_registry: LunarRegistry):
    deps = set()
    for comp in components:
        registered_component = lunar_registry.get_by_class_name(
            comp.class_name
        )
        if registered_component is None:
            raise ComponentError(
                f"Failed to locate component package for {comp.class_name}"
            )

        if comp.class_name == Subworkflow.__name__:
            try:
                subworkflow_input = [inp.value for inp in comp.inputs if inp.key.lower() == "workflow"][0]
            except IndexError:
                raise ComponentError(f"Expected ine subworkflow as input `workflow`.")

            subworkflow_input = WorkflowModel.model_validate(subworkflow_input)
            deps.update(gather_component_dependencies(subworkflow_input.components, lunar_registry))
            continue

        deps.update(registered_component.component_requirements)
        deps.update(comp.get_python_coder_deps())
    return list(deps)


async def run_component_as_prefect_flow(
    lunar_registry: LunarRegistry, component_path: str, 
    venv: Optional[str] = None, environment: Optional[Dict] = None
):

    if venv is None:
        flow = component_to_prefect_flow(component_path, lunar_registry)
        flow_result = flow(component_path, return_state=True)
        if flow_result.is_cancelled():
            flow_result = await gather_partial_flow_results(
                str(flow_result.state_details.flow_run_id)
            )
        else:
            flow_result = await flow_result.data.get()

        return flow_result
    with open(component_path, "r") as w:
        component = json.load(w)

    component = ComponentModel.model_validate(component)

    deps = gather_component_dependencies([component], lunar_registry)

    process = await PythonProcess.create(
        venv_path=venv,
        command=create_base_command() + ["--component", component_path],
        expected_packages=deps,
        stream_output=True,
        env=environment,
    )

    with OutputCatcher() as output:
        _ = await process.run()


    return parse_component_result(output)


async def run_workflow_as_prefect_flow(
    lunar_registry: LunarRegistry,
    workflow_path: str,
    venv: Optional[str] = None,
    environment: Optional[Dict] = {},
    event_dispatcher: EventDispatcher = None
):
    if not Path(workflow_path).is_file():
        raise RuntimeError(f"Workflow file {workflow_path} not found!")

    if venv is None:
        flow = workflow_to_prefect_flow(workflow_path, lunar_registry=lunar_registry)
        flow_result = flow(workflow_path, return_state=True)
        if flow_result.is_cancelled():
            flow_result = await gather_partial_flow_results(
                str(flow_result.state_details.flow_run_id)
            )
        else:
            flow_result = await flow_result.data.get()

        return flow_result

    with open(workflow_path, "r") as w:
        workflow = json.load(w)
    workflow = WorkflowModel.model_validate(workflow)
    deps = gather_component_dependencies(workflow.components, lunar_registry)

    process = await PythonProcess.create(
        venv_path=venv,
        command=create_base_command() + [workflow_path],
        expected_packages=deps,
        stream_output=True,
        env=environment,
    )

    # LUNAR_CONTEXT.lunar_registry.update_workflow_runtime(workflow_id=workflow.id, workflow_pid=process)

    async def capture_workflow_outputs(data):
        while True:
            output_lines_list = data._stringio.getvalue().splitlines()
            component_json = parse_component_result(output_lines_list)
            if event_dispatcher is not None:
                event_dispatcher.dispatch_component_output_event(component_json)
            await asyncio.sleep(1)
            if WORKFLOW_OUTPUT_END in output_lines_list:
                break

    with OutputCatcher() as output:
        # _ = await process.run()
        await asyncio.gather(process.run(), capture_workflow_outputs(output))

    parsed_output = parse_component_result(output)
    return parsed_output


def compose_component_result(result: Dict):
    try:
        for cmp, cmp_out in result.items():
            if isinstance(cmp_out, ComponentModel):
                return json.dumps(cmp_out.model_dump(by_alias=True), cls=ComponentEncoder)
    except Exception as e:
        raise ComponentError(f"Failed to parse component output: {result}: {str(e)}")
    # json_out = f"{RUN_OUTPUT_START}"
    # json_out = json.dumps(result, cls=ComponentEncoder)
    # json_out += f"{RUN_OUTPUT_END}"

    # return json_out


def parse_component_result(process_output_lines: List):
    previous_output_line = None
    parsed_components = {}
    for process_output_line in process_output_lines:
        if previous_output_line == RUN_OUTPUT_START:
            component_label = None
            json_component_result = {}
            try:
                json_component_result = json.loads(process_output_line)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse result as JSON! Details: {str(e)}")
            except KeyError:
                logger.error(f"Failed to parse component label from result: {process_output_line}")
            except Exception as e:
                logger.error(f"Unexpected error while parsing component result: {str(e)}")
            if "label" in json_component_result:
                component_label = json_component_result["label"]
            try:
                component_model_result = ComponentModel.model_validate(json_component_result)
            except Exception as e:
                component_model_result = json_component_result
                logger.error(f"Failed to parse component output: {json_component_result}. Error: {str(e)}")
            parsed_components[component_label] = component_model_result

        previous_output_line = process_output_line
    return parsed_components


parser = argparse.ArgumentParser(
    prog="engine",
    description="Entrypoint for Lunarverse CLI.",
    epilog="Thanks for using Lunarverse!",
)
parser.add_argument(
    "--venv", required=False, action="store", help="Run workflow within this venv."
)

parser.add_argument(
    "--component", required=False, action="store_true", help="Expect a component"
)

parser.add_argument(
    "json_path", help="The workflow/component json or its filesystem location."
)

if __name__ == "__main__":
    # DO NOT remove this __main__ section

    # import time

    import asyncio
    from lunarbase import lunar_context_factory

    args = parser.parse_args()
    lunar_context = lunar_context_factory()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    if args.component:
        result = loop.run_until_complete(
            run_component_as_prefect_flow(
                lunar_registry=lunar_context.lunar_registry,
                component_path=args.json_path, venv=args.venv
            )
        )
        print(f"{RUN_OUTPUT_START}")
        result_out = compose_component_result(result)
        print(result_out)  # This is to have a return
        print(f"{RUN_OUTPUT_END}")
    else:
        print(f"{WORKFLOW_OUTPUT_START}", flush=True)
        st = time.time()
        result = loop.run_until_complete(
            run_workflow_as_prefect_flow(
                lunar_registry=lunar_context.lunar_registry,
                workflow_path=args.json_path, 
                venv=args.venv
            )
        )
        print(f"{WORKFLOW_OUTPUT_END}", flush=True)
        et = time.time() - st
        logger.info(f"Workflow Runtime: {et} seconds.")
