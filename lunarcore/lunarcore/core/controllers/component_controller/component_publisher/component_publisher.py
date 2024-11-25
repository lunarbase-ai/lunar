# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from lunarcore.utils.config_generator import ComponentSetupGenerator


class PublisherService:

    def create_pull_request(
            self,
            component_name: str,
            new_branch_name: str,
            component_class: str,
            component_documentation: Optional[str]
    ):
        raise NotImplementedError()


class ComponentPublisher:
    def __init__(self, publisher: PublisherService):
        self.publisher = publisher

    def publish_component(
            self,
            component_name: str,
            component_description: str,
            component_class: str,
            component_documentation: str,
            version: str
    ):
        #TODO: Validate

        component_generator = ComponentSetupGenerator(
            name=component_name,
            description=component_description,
            version=version,

        )

        self.publisher.create_pull_request(
            component_name=component_name,
            new_branch_name=f"component-submission/{component_name.replace(' ','_').lower()}",
            component_class=component_class,
            component_documentation=component_documentation
        )
