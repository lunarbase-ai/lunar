# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List

from lunarbase.controllers.component_controller import (
    ComponentController,
)
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.data_models import ComponentModel


class ComponentAPI:
    def __init__(self, component_controller:ComponentController):
        self.component_controller = component_controller

    def index_global(self):
        return self.component_controller.index_global_components()

    def list_all(self, user_id):
        return self.component_controller.list_all_components(user_id)

    def get_by_id(self, component_id: str, user_id: str):
        return self.component_controller.get_by_id(component_id, user_id)

    def create_custom_component(self, component: ComponentModel, user_id: str):
        try:
            return self.component_controller.save(component, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    def save_auto_custom_components(
        self, components: List[ComponentModel], user_id: str
    ):
        try:
            return self.component_controller.save_auto_custom_components(
                components, user_id
            )
        except Exception as e:
            raise ComponentError(str(e))

    def delete_custom_component(self, component_id: str, user_id: str):
        try:
            return self.component_controller.delete(component_id, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    async def run(self, component: ComponentModel, user_id: str):
        return await self.component_controller.run(component, user_id)

    def search(self, query: str, user_id: str):
        try:
            return self.component_controller.search(query, user_id)
        except Exception as e:
            raise ComponentError(str(e))

    def get_example_workflow_by_label(self, label: str, user_id: str):
        return self.component_controller.get_example_workflow_by_label(
            label=label, user_id=user_id
        )

    def publish_component(
        self,
        component_name: str,
        component_class: str,
        component_documentation: str,
        access_token: str,
        user_id: str,
    ):
        return self.component_controller.publish_component(
            component_name=component_name,
            component_class=component_class,
            component_documentation=component_documentation,
            access_token=access_token,
            user_id=user_id,
        )
