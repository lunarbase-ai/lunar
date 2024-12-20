# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Union, Dict, List

from lunarbase.config import LunarConfig
from lunarbase.controllers.workflow_controller import WorkflowController
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.auto_workflow import AutoWorkflow


class WorkflowAPI:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self.workflow_controller = WorkflowController(config=config)

    def list_all(self, user_id):
        return self.workflow_controller.list_all(user_id)

    def get_by_id(self, workflow_id: str, user_id: str):
        return self.workflow_controller.get_by_id(workflow_id, user_id)

    def list_short(self, user_id: str):
        return self.workflow_controller.list_short(user_id)

    def search(
        self,
        user_id: str,
        query: str = "",
    ):
        return self.workflow_controller.search(query=query, user_id=user_id)

    def save(self, user_id: str, workflow: Optional[WorkflowModel] = None):
        return self.workflow_controller.save(user_id=user_id, workflow=workflow)

    def auto_create(self, auto_workflow: AutoWorkflow, user_id: str):
        return self.workflow_controller.auto_create(auto_workflow, user_id)

    def auto_modify(
        self, auto_workflow: AutoWorkflow, instruction: str, user_id: str
    ):
        return self.workflow_controller.auto_modify(
            auto_workflow, instruction, user_id
        )

    def update(self, workflow: WorkflowModel, user_id: str):
        return self.workflow_controller.update(workflow, user_id)

    def delete(self, workflow_id: str, user_id: str):
        return self.workflow_controller.delete(workflow_id, user_id)

    def cancel(self, workflow_id: str, user_id: str):
        return self.workflow_controller.cancel(workflow_id, user_id)

    async def run(self, workflow: WorkflowModel, user_id: str):
        return await self.workflow_controller.run(workflow, user_id)

    async def get_workflow_component_inputs(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.get_workflow_component_inputs(workflow_id, user_id)

    async def get_workflow_component_outputs(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.get_workflow_component_outputs(workflow_id, user_id)

    async def run_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        return await self.workflow_controller.run_workflow_by_id(workflow_id, workflow_inputs, user_id)
