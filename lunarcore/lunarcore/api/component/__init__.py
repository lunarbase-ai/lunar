# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Union, Dict, List

from lunarcore.config import LunarConfig
from lunarcore.core.controllers.component_controller import ComponentController
from lunarcore.errors import ComponentError
from lunarcore.core.data_models import ComponentModel


class ComponentAPI:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self.component_controller = ComponentController(config=config)

    async def index_global(self):
        return await self.component_controller.index_global_components()

    async def list_all(self, user_id):
        return await self.component_controller.list_all_components(user_id)

    async def get_by_id(self, component_id: str, user_id: str):
        return await self.component_controller.get_by_id(component_id, user_id)

    async def create_custom_component(self, component: ComponentModel, user_id: str):
        try:
            return await self.component_controller.save(component, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    async def save_auto_custom_components(
        self, components: List[ComponentModel], user_id: str
    ):
        try:
            return await self.component_controller.save_auto_custom_components(
                components, user_id
            )
        except Exception as e:
            raise ComponentError(str(e))

    async def delete_custom_component(self, component_id: str, user_id: str):
        try:
            return await self.component_controller.delete(component_id, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    async def run(self, component: ComponentModel, user_id: str):
        return await self.component_controller.run(component, user_id)

    async def search(self, query: str, user_id: str):
        try:
            return await self.component_controller.search(query, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    async def get_example_workflow_by_label(self, label: str, user_id: str):
        return await self.component_controller.get_example_workflow_by_label(
            label=label, user_id=user_id
        )
