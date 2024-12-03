# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import logging
import os
import shutil
import warnings

from dotenv import load_dotenv
from fastapi import UploadFile
from typing import Dict, List

from lunarcore.benchmark.auto_workflow.autoworkflow_tester.config import (
    DOTENV_PATH,
    AUTOWORKFLOW_LABEL,
    COMPONENT_OUTPUT_KEY,
    COMPONENT_OUTPUT_VALUE_KEY,
    COMPONENT_IS_TERMINAL_KEY,
    USER_ID,
    EXECUTION_TIMEOUT,
)
from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.auto_workflow import AutoWorkflow
from lunarcore.core.controllers.file_controller import FileController
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel
from lunarcore.core.typings.datatypes import File
from lunarcore.benchmark.auto_workflow.tester import Tester


class AutoworkflowTester(Tester):
    def __init__(self, env_path: str, save_workflows: bool = False, logger: logging.Logger = None):
        super().__init__(tester_name=AUTOWORKFLOW_LABEL, logger=logger)
        self.workflow_controller=WorkflowController(env_path)
        self.file_controller=FileController(env_path)
        self.save_workflows = save_workflows  # Note: save_workflows==True ==> not deleting created workflows ==> risk of memory gets full if not cleaning up regularly
        if len(COMPONENT_REGISTRY.components) == 0:
            asyncio.run(COMPONENT_REGISTRY.register(fetch=True))

    def _terminal_outputs(self, component_dir: Dict[str, Dict]):
        out = []
        for component in component_dir.values():
            if component[COMPONENT_IS_TERMINAL_KEY]:
                out.append(component[COMPONENT_OUTPUT_KEY][COMPONENT_OUTPUT_VALUE_KEY])
        return out

    def _create_auto_workflow(self, test_name: str, description: str):
        workflow = WorkflowModel(
            # id="19c07004-8794-4475-a660-8529bbd61663",
            user_id=USER_ID,
            name=test_name,
            description=description,
            components=[],
            timeout=EXECUTION_TIMEOUT
        )
        auto_workflow = AutoWorkflow(workflow=workflow)
        return auto_workflow

    def _clear_venv(self, workflow: WorkflowModel, user_id: str = USER_ID):
        venv_dir = os.path.join(
            self.workflow_controller.config.LUNAR_STORAGE_BASE_PATH,
            self.workflow_controller.config.USER_DATA_PATH,
            user_id,
            self.workflow_controller.config.USER_WORKFLOW_ROOT,
            workflow.id,
        )
        if os.path.exists(venv_dir):
            shutil.rmtree(venv_dir)
        else:
            warnings.warn(f"Path '{venv_dir}' does not exist. Skipping deleting workflow!")

    def _save_workflow_files(self, workflow_id: str, files: List[File]):
        for file in files:
            try:
                upload_file = UploadFile(filename=os.path.basename(file.path), file=open(file.path, 'rb'))
                asyncio.run(self.file_controller.save(workflow_id, upload_file, file.path))
            except Exception as e:
                warnings.warn(f'Could not upload file {file.path} to workflow_id {workflow_id}')

    def _save_workflow(self, workflow: WorkflowModel, user_id: str = USER_ID):
        try:
            asyncio.run(self.workflow_controller.save(workflow, user_id))
        except Exception as e:
            warnings.warn(f'Could not save workflow {workflow.id}')

    def run_test(self, test_name: str, intent: str, files: List[File], user_id=USER_ID):
        self.logger.info(f"Starting test '{test_name}'")
        auto_workflow = self._create_auto_workflow(test_name, intent)
        self.logger.info(f'Auto-generating workflow {auto_workflow.workflow.id}')
        workflow = auto_workflow.generate_workflow(files)
        self.logger.debug(f'Generated the following workflow:\n{workflow.json()}')
        self.logger.info(f'Executing workflow...')
        if self.save_workflows:
            self._save_workflow(workflow)
            self._save_workflow_files(workflow.id, files)
        run_result = asyncio.run(self.workflow_controller.run(workflow, user_id))
        self.logger.debug(f'Result: {run_result}')
        if not self.save_workflows:
            self._clear_venv(workflow)
        workflow_outputs = [str(x) for x in self._terminal_outputs(run_result)]
        self.logger.info(f'Got workflow output: {workflow_outputs}')
        return workflow_outputs


def run_test(env_path: str = DOTENV_PATH, save_workflows: bool = False,
             test_name: str = 'test name',
             intent: str = 'Output the string "abc123" reversed.',
             files: List[File] = None):
    auto_workflow_tester = AutoworkflowTester(env_path, save_workflows)
    files = files or []
    auto_workflow_tester.run_test(test_name, intent, files)


if __name__ == "__main__":
    load_dotenv(DOTENV_PATH)
    run_test()
