# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.data_types import DataType
from lunarcore.data_sources import DataSourceType

### GLOBAL VARS TO USE WITH COMPONENTS ###

COMPONENT_DESCRIPTION_TEMPLATE = """
<describe the component in a single sentence>
Output (<type of the output (e.g., List[str])>): <describe the component output in detail>
""".strip()


class LunarComponent(ABC):
    component_name: str = None
    component_description: str = COMPONENT_DESCRIPTION_TEMPLATE
    input_types: Dict[str, DataType] = None
    data_source_types: Dict[str, DataSourceType] = None
    output_type: DataType = None
    component_group: ComponentGroup = ComponentGroup.LUNAR
    default_configuration: Dict = None

    def __init_subclass__(
        cls,
        component_name: str,
        input_types: Dict[str, DataType],
        output_type: DataType,
        component_group: ComponentGroup = ComponentGroup.LUNAR,
        component_description: str = COMPONENT_DESCRIPTION_TEMPLATE,
        **kwargs,
    ):
        cls.component_name = component_name
        cls.component_description = component_description
        cls.input_types = input_types
        cls.data_source_types = kwargs.get("data_source_types", {})
        kwargs.pop("data_source_types", None)
        cls.output_type = output_type
        cls.component_group = component_group
        cls.default_configuration = kwargs
        super().__init_subclass__()

    def __init__(
        self,
        configuration: Optional[Dict] = None,
    ):
        self.connections = dict()
        self.configuration = dict()
        self.configuration.update(configuration or self.__class__.default_configuration)

    @abstractmethod
    def run(
        self,
        **inputs: Any,
    ):
        pass
