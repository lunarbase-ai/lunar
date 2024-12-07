# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Union, Dict, List

from lunarcore.config import LunarConfig
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel
from lunarcore.core.auto_workflow import AutoWorkflow


class WorkflowAPI:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self.workflow_controller = WorkflowController(config=config)

    async def list_all(self, user_id):
        return await self.workflow_controller.list_all(user_id)

    async def get_by_id(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.get_by_id(workflow_id, user_id)

    async def list_short(self, user_id: str):
        return await self.workflow_controller.list_short(user_id)

    async def search(
        self,
        user_id: str,
        query: str = "",
    ):
        return await self.workflow_controller.search(query=query, user_id=user_id)

    async def save(self, user_id: str, workflow: Optional[WorkflowModel] = None):
        return await self.workflow_controller.save(user_id=user_id, workflow=workflow)

    async def auto_create(self, auto_workflow: AutoWorkflow, user_id: str):
        return await self.workflow_controller.auto_create(auto_workflow, user_id)

    async def auto_modify(
        self, auto_workflow: AutoWorkflow, instruction: str, user_id: str
    ):
        return await self.workflow_controller.auto_modify(
            auto_workflow, instruction, user_id
        )

    async def update(self, workflow: WorkflowModel, user_id: str):
        return await self.workflow_controller.update(workflow, user_id)

    async def delete(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.delete(workflow_id, user_id)

    async def cancel(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.cancel(workflow_id, user_id)

    async def run(self, workflow: WorkflowModel, user_id: str):
        return await self.workflow_controller.run(workflow, user_id)

    async def get_workflow_component_inputs(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.get_workflow_component_inputs(workflow_id, user_id)

    async def get_workflow_component_outputs(self, workflow_id: str, user_id: str):
        return await self.workflow_controller.get_workflow_component_outputs(workflow_id, user_id)

    async def run_workflow_by_id(self, workflow_id: str, workflow_inputs: List[Dict], user_id: str):
        return await self.workflow_controller.run_workflow_by_id(workflow_id, workflow_inputs, user_id)
