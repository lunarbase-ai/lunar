# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List, Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from lunarcore.core.data_models import WorkflowModel


class ChatRequestBody(BaseModel):
    messages: List[Any] = []
    workflows: List[str] = []
