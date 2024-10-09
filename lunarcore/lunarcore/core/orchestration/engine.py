# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import importlib
import json
import os.path
import re
from collections import deque
from datetime import timedelta
from typing import Optional, List, Dict, Union

from prefect import task, Flow
from prefect.futures import PrefectFuture
from prefect.task_runners import ConcurrentTaskRunner

from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.component import BaseComponent
from lunarcore.core.component.core_components.subworkflow import Subworkflow
from lunarcore.core.orchestration.callbacks import crashed_flow_handler, running_flow_handler
from lunarcore.core.orchestration.process import (
    PythonProcess,
    create_base_command,
    OutputCatcher,
)
from lunarcore.core.orchestration.task_promise import TaskPromise
from lunarcore.errors import ComponentError
from lunarcore.core.data_models import (
    ComponentModel,
    WorkflowModel,
    ComponentEncoder,
)
from lunarcore.core.typings.datatypes import DataType
from lunarcore.utils import setup_logger

MAX_RESULT_DICT_LEN = 10
MAX_RESULT_DICT_DEPTH = 2

RUN_OUTPUT_START = "<OUTPUT RESULT>"
RUN_OUTPUT_END = "<OUTPUT RESULT END>"

logger = setup_logger("orchestration-engine")

def assemble_component_type(component: ComponentModel):
    def constructor(
        self,
        model: Optional[ComponentModel] = None,
        configuration: Optional[Dict] = None,
    ):
        super(self.__class__, self).__init__(model=model, configuration=configuration)

    _class = type(
        component.class_name,
        (BaseComponent,),
        {"__init__": constructor, **component.get_callables()},
        component_name=component.name,
        component_description=component.description,
        input_types={inp.key: inp.data_type for inp in component.inputs},
        output_type=component.output.data_type,
        component_group=component.group,
    )
    return _class


def component_factory(component: ComponentModel):
    if component.get_component_code() is not None and not os.path.isfile(
        component.get_component_code()
    ):
        task_class = assemble_component_type(component)
        task_instance = task_class(model=component)
        return task_instance
    try:
        pkg_comp = COMPONENT_REGISTRY.get_by_class_name(component.class_name)
        if pkg_comp is None:
            raise ComponentError(
                f"Error encountered while trying to load {component.class_name}! "
                f"Component not found  in {COMPONENT_REGISTRY.get_component_names()}. "
                f"Registry loaded from {COMPONENT_REGISTRY.registry_root}."
            )
        component_module, _ = pkg_comp

        component_module = importlib.import_module(component_module)
        task_class = getattr(component_module, component.class_name)
        task_instance = task_class(model=component)
    except Exception as e:
        raise ComponentError(f"{component.label}: {str(e)}")
    return task_instance


def generate_prefect_cache_key(context, arguments):
    component = arguments.get("component_instance").component_model
    _key = f"{context.task.task_key}-{context.task.fn.__code__.co_code.hex()[:15]}-{component.label}-{'_'.join([str(hash(c_input)) for c_input in component.inputs])}"
    return _key


@task(cache_key_fn=generate_prefect_cache_key, cache_expiration=timedelta(minutes=10))
def run_prefect_task(
    component_instance: BaseComponent,
):
    try:
        result = component_instance.run_in_workflow()
    except Exception as e:
        raise ComponentError(str(e))

    return result


@task(refresh_cache=True, persist_result=False)
def stream_prefect_task(
    component_instance: BaseComponent,
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
        current_model = component_instance.component_model
        for (link_key, link_template), promised_model in zip(links, results):
            current_model = update_inputs(
                current_task=current_model,
                upstream_task=promised_model,
                upstream_label=promised_model.label,
                input_key=link_key,
                template_key=link_template,
            )
        component_instance.component_model = current_model
        try:
            result = component_instance.run_in_workflow()
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
            obj = component_factory(tasks[next_task])
        except ComponentError as e:
            real_tasks[next_task] = e
            logger.error(f"Error running {tasks[next_task].label}: {str(e)}")
            continue

        if isinstance(obj, Subworkflow):

            @task()
            def assign_output(model, output):
                model.output = output
                return model

            subworkflow = obj.validate()
            _tasks = create_flow_dag(subworkflow)
            for subsid, substate in _tasks.items():
                subresult = run_step(substate)

                if isinstance(subresult, ComponentError):
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
                name=f"Task {obj.component_model.name}",
                refresh_cache=obj.disable_cache,
                persist_result=True,
            ).submit(
                component_instance=obj,
                wait_for=upstream,
            )

    return real_tasks


def run_step(step: Union[PrefectFuture, ComponentError]):
    if isinstance(step, ComponentError):
        return step
    try:
        result = step.result(raise_on_failure=True)
    except ComponentError as e:
        result = e

    return result


def create_flow(
    flow: WorkflowModel,
    flow_path: Optional[str] = None,
):
    if flow_path is not None:
        # TODO: check flow_path existence
        with open(flow_path, "r") as f:
            flow_data = json.loads(f.read())
        flow = WorkflowModel.model_validate(flow_data)

    tasks = create_flow_dag(flow)

    states_id = list(tasks.keys())
    results = {}
    for sid in states_id:
        if isinstance(tasks[sid], TaskPromise):
            results[sid] = tasks[sid].component.component_model
            continue
        results[sid] = run_step(tasks[sid])

    return results


def create_task_flow(
    component: ComponentModel,
):
    try:
        obj = component_factory(component)
        if isinstance(obj, Subworkflow):
            subworkflow = obj.validate()
            result = None
            for _, subresult in create_flow(subworkflow).items():
                if subresult.is_terminal:
                    component.output = subresult.output
                    result = component
                    break
        else:
            prefect_task = run_prefect_task.with_options(
                name=f"Task {component.name}",
                refresh_cache=obj.disable_cache,
            ).submit(
                component_instance=obj,
                wait_for=None,
            )
            result = run_step(prefect_task)
    except ComponentError as e:
        logger.error(f"Error running {component.label}: {str(e)}")
        result = e

    return {component.label: result}


def component_to_prefect_flow(
    component: ComponentModel,
) -> Flow:
    return Flow(
        fn=create_task_flow,
        name=component.name,
        flow_run_name=component.id,
        description=component.description,
        version=component.version,
        timeout_seconds=component.timeout,
        task_runner=ConcurrentTaskRunner(),
        validate_parameters=False,
    )


def workflow_to_prefect_flow(
    workflow: WorkflowModel,
):
    return Flow(
        fn=create_flow,
        name=workflow.name,
        flow_run_name=workflow.id,
        description=workflow.description,
        version=workflow.version,
        timeout_seconds=workflow.timeout,
        task_runner=ConcurrentTaskRunner(),
        validate_parameters=False,
        on_running=[running_flow_handler]
    )


async def run_component_as_prefect_flow(
    component: str,
    venv: Optional[str] = None,
    environment: Optional[Dict] = None
):
    component_str = component
    if os.path.isfile(component_str):
        with open(component_str, "r") as w:
            component = json.load(w)
    else:
        component = json.loads(component_str)

    component = ComponentModel.model_validate(component)
    if venv is None:
        flow = component_to_prefect_flow(component)
        return flow(component)

    process = await PythonProcess.create(
        venv_path=venv,
        command=create_base_command() + ["--component", component_str],
        expected_packages=component.component_code_requirements,
        stream_output=True,
        env=environment
    )

    with OutputCatcher() as output:
        _ = await process.run()

    return parse_component_result(output)


async def run_workflow_as_prefect_flow(
    workflow: str,
    venv: Optional[str] = None,
    environment: Optional[Dict] = None
):
    workflow_str = workflow
    if os.path.isfile(workflow_str):
        with open(workflow_str, "r") as w:
            workflow = json.load(w)
    else:
        workflow = json.loads(workflow_str)

    workflow = WorkflowModel.model_validate(workflow)
    if venv is None:
        flow = workflow_to_prefect_flow(workflow)

        return flow(workflow)

    deps = set()
    for comp in workflow.components:
        deps.update(comp.component_code_requirements)

    process = await PythonProcess.create(
        venv_path=venv,
        command=create_base_command() + [workflow_str],
        expected_packages=list(deps),
        stream_output=True,
        env=environment
    )

    with OutputCatcher() as output:
        _ = await process.run()

    return parse_component_result(output)


def compose_component_result(result: Dict):
    for cmp, cmp_out in result.items():
        if isinstance(cmp_out, ComponentModel):
            result[cmp] = cmp_out.model_dump(by_alias=True)
    json_out = f"{RUN_OUTPUT_START}"
    json_out += json.dumps(result, cls=ComponentEncoder)
    json_out += f"{RUN_OUTPUT_END}"

    return json_out


def parse_component_result(result: List):
    expected_output = None
    for out in result:
        if RUN_OUTPUT_START in out and RUN_OUTPUT_END in out:
            pattern = re.compile(
                f"{RUN_OUTPUT_START}(.*){RUN_OUTPUT_END}", re.MULTILINE
            )
            match = re.search(pattern, out)
            try:
                expected_output = match.group(1)
            except IndexError:
                continue
            break

    if expected_output is None:
        raise ComponentError(
            f"Something went wrong while running flow. See server logs for details."
        )

    try:
        result = json.loads(expected_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse result as JSON! Details: {str(e)}")

    for sid, component_result in result.items():
        try:
            component_result = ComponentModel.parse_raw(component_result)
            result[sid] = component_result
        except Exception:
            continue

    return result


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

    args = parser.parse_args()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    if len(COMPONENT_REGISTRY.components) == 0:
        loop.run_until_complete(COMPONENT_REGISTRY.load_components())

    if args.component:
        result = loop.run_until_complete(
            run_component_as_prefect_flow(args.json_path, venv=args.venv)
        )
    else:
        # st = time.time()
        result = loop.run_until_complete(
            run_workflow_as_prefect_flow(args.json_path, venv=args.venv)
        )
        # et = time.time() - st
        # print(f"Runtime: {et} seconds.")
    result_out = compose_component_result(result)
    print(result_out)  # This is to have a return
