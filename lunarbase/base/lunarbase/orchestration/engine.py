# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import time
import asyncio
import argparse
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional

from lunarbase.components.component_wrapper import ComponentWrapper
from lunarbase.components.subworkflow import Subworkflow
from lunarbase.orchestration.process import (
    OutputCatcher,
    PythonProcess,
    create_base_command,
)

from lunarbase.orchestration.prefect_orchestrator import PrefectOrchestrator
from lunarbase.orchestration.task_promise import TaskPromise
from lunarbase.orchestration.utils import update_inputs
from lunarbase.utils import setup_logger
from lunarcore.component.data_types import DataType
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.component_encoder import ComponentEncoder
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel
from lunarbase.registry import LunarRegistry
from lunarbase.config import LunarConfig

from lunarbase.domains.workflow.event_dispatcher import EventDispatcher
from lunarbase.domains.datasources.controllers import DataSourceController

MAX_RESULT_DICT_LEN = 10
MAX_RESULT_DICT_DEPTH = 2

RUN_OUTPUT_START = "<COMPONENT OUTPUT START>"
RUN_OUTPUT_END = "<COMPONENT OUTPUT END>"

WORKFLOW_OUTPUT_START = "<WORKFLOW OUTPUT START>"
WORKFLOW_OUTPUT_END = "<WORKFLOW OUTPUT END>"

logger = setup_logger("orchestration-engine")


class LunarEngine:
    def __init__(
        self,
        config: LunarConfig,
        datasource_controller: DataSourceController,
        orchestrator: PrefectOrchestrator
    ):
        self._config = config
        self._orchestrator = orchestrator
        self._datasource_controller = datasource_controller

    async def run_workflow(
            self,
            lunar_registry: LunarRegistry,
            workflow_path: str,
            venv: Optional[str] = None,
            environment: Optional[Dict] = {},
            event_dispatcher: EventDispatcher = None
    ):
        if not Path(workflow_path).is_file():
            raise RuntimeError(f"Workflow file {workflow_path} not found!")

        if venv is None:
            def flow_function(*args, **kwargs):
                return self._create_flow(
                    *args,
                    lunar_registry=lunar_registry,
                    event_dispatcher=event_dispatcher,
                    **kwargs
                )

            with open(workflow_path, "r") as w:
                workflow = json.load(w)

            workflow = WorkflowModel.model_validate(workflow)
            flow = self._orchestrator.map_workflow_to_prefect_flow(
                flow_function,
                workflow,
            )
            flow_result = flow(workflow_path, return_state=True)
            if flow_result.is_cancelled():
                flow_result = await self._gather_partial_flow_results(
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

        async def capture_workflow_outputs(data):
            prev_output_line_list_len = 0
            while True:
                output_lines_list = data._stringio.getvalue().splitlines()
                component_json = parse_component_result(output_lines_list)
                if event_dispatcher is not None and len(component_json) > 0 and prev_output_line_list_len != len(
                        output_lines_list):
                    event_dispatcher.dispatch_components_output_event(component_json)
                prev_output_line_list_len = len(output_lines_list)
                await asyncio.sleep(1)
                if WORKFLOW_OUTPUT_END in output_lines_list:
                    break

        with OutputCatcher() as output:
            await asyncio.gather(process.run(), capture_workflow_outputs(output))

        parsed_output = parse_component_result(output)
        return parsed_output

    def _create_flow_dag(
            self,
            workflow: WorkflowModel,
            lunar_registry: LunarRegistry,
            event_dispatcher: EventDispatcher = None,
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

                upstream_result = self._orchestrator.run_step(real_tasks[pred])
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
                obj = ComponentWrapper(
                    component=tasks[next_task], 
                    lunar_registry=lunar_registry, 
                    datasource_controller=self._datasource_controller
                )
            except ComponentError as e:
                real_tasks[next_task] = e
                if event_dispatcher is not None:
                    event_dispatcher.dispatch_components_output_event(
                        {"workflow_id": tasks[next_task].workflow_id, "outputs": {tasks[next_task].label: str(e)}}
                    )
                logger.error(f"Error running {tasks[next_task].label}:{str(e)}", exc_info=True)
                continue
            if obj.component_model.class_name == Subworkflow.__name__:
                subworkflow = Subworkflow.subworkflow_validation(obj.component_model)
                _tasks = self._create_flow_dag(subworkflow, lunar_registry=lunar_registry, event_dispatcher=event_dispatcher)
                error = None
                for subsid, substate in _tasks.items():
                    subresult = self._orchestrator.run_step(substate)

                    if isinstance(subresult, ComponentError):
                        # Only show the first subworkflow error
                        if error is None:
                            error = subresult
                            real_tasks[next_task] = subresult
                        continue

                    if subresult.is_terminal:
                        real_tasks[next_task] = self._orchestrator.assign_output(
                            tasks[next_task], subresult.output
                        )
                        break
            elif len(promises[next_task]) > 0:
                real_tasks[next_task] = self._orchestrator.stream_task(
                    obj, promises[next_task], next_task, upstream=upstream
                )
            else:
                if obj.component_model.output.data_type == DataType.STREAM:
                    try:
                        next(dag.successors(next_task))
                        real_tasks[next_task] = TaskPromise(obj)
                        continue
                    except StopIteration:
                        pass
                real_tasks[next_task] = self._orchestrator.run_task(obj, upstream=upstream)
        return real_tasks

    def _create_flow(self, workflow_path: str, lunar_registry: LunarRegistry, event_dispatcher: EventDispatcher = None):
        with open(workflow_path, "r") as w:
            workflow = json.load(w)
        workflow = WorkflowModel.model_validate(workflow)
        tasks = self._create_flow_dag(workflow, lunar_registry=lunar_registry, event_dispatcher=event_dispatcher)
        states_id = list(tasks.keys())
        results = {}
        for sid in states_id:
            if isinstance(tasks[sid], TaskPromise):
                results[sid] = tasks[sid].component.component_model
                continue
            results[sid] = self._orchestrator.run_step(tasks[sid])
            print(f"{RUN_OUTPUT_START}", flush=True)
            if isinstance(results[sid], ComponentError):
                print(f"{sid}:{str(results[sid])}", flush=True)
            else:
                json_out = json.dumps(results[sid], cls=ComponentEncoder)
                print(f"{json_out}", flush=True)
            print(f"{RUN_OUTPUT_END}", flush=True)
        return results

    async def _gather_partial_flow_results(self, flow_run_id: str):
        current_task_results = dict()
        current_task_runs = self._orchestrator.get_task_runs(flow_run_id)
        for tr in current_task_runs or []:
            if tr.state.is_completed():
                _result = tr.state.result(raise_on_failure=False).get()
                current_task_results[_result.label] = _result
            else:
                _result = ComponentError(f"{tr.state.name}:{tr.state.message}!")
                current_task_results[tr.name] = _result
        return current_task_results


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


def parse_component_result(process_output_lines: List):
    previous_output_line = None
    parsed_components = {}
    for process_output_line in process_output_lines:
        if process_output_line == WORKFLOW_OUTPUT_END:
            break
        if (
            process_output_line == RUN_OUTPUT_START or
            process_output_line == RUN_OUTPUT_END or
            process_output_line == WORKFLOW_OUTPUT_END or
            process_output_line == WORKFLOW_OUTPUT_START
        ):
            previous_output_line = process_output_line
            continue
        if previous_output_line == RUN_OUTPUT_START:
            component_label = None
            json_component_result = {}
            try:
                json_component_result = json.loads(process_output_line)
            except json.JSONDecodeError as e:
                try:
                    component_label = process_output_line.split(':', 1)[0]
                    error_message = process_output_line.split(':', 1)[1]
                    parsed_components[component_label] = error_message
                    continue
                except Exception as e:
                    logger.error(f"Failed to parse JSON or component label from result:{process_output_line}")
            except Exception as e:
                logger.error(f"Unexpected error while parsing component result:{str(e)}")
            if "label" in json_component_result:
                component_label = json_component_result["label"]
            try:
                component_model_result = ComponentModel.model_validate(json_component_result)
            except Exception as e:
                component_model_result = json_component_result
                logger.error(f"Failed to parse component output! {component_label}:{json_component_result}. Error: {str(e)}")
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
    import asyncio
    from lunarbase import lunar_context_factory
    from lunarbase.config import LunarConfig

    args = parser.parse_args()
    lunar_context = lunar_context_factory()
    engine = lunar_context.lunar_engine

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    print(f"{WORKFLOW_OUTPUT_START}", flush=True)
    st = time.time()
    result = loop.run_until_complete(
        engine.run_workflow(
            lunar_registry=lunar_context.lunar_registry,
            workflow_path=args.json_path,
            venv=args.venv
        )
    )
    print(f"{WORKFLOW_OUTPUT_END}", flush=True)
    et = time.time() - st
    logger.info(f"Workflow Runtime: {et} seconds.")
