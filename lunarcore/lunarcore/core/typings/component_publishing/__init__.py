# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pydantic import BaseModel

from lunarcore.core.typings.components import ComponentGroup
from lunarcore.core.typings.datatypes import DataType
from lunarcore.utils import to_camel


class ComponentPublishingInput(BaseModel):
    component_name: str
    component_class: str
    component_documentation: str
    access_token: str
    user_id: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        arbitrary_attributes_allowed = True
        json_encoders = {
            DataType: lambda out_type: str(out_type.name),
            ComponentGroup: lambda group: str(group.name),
        }
        validate_assignment = True
