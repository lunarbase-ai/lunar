#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import asyncio

from typing import Dict, Union

from lunarbase.modeling.data_models import ComponentModel


class EventDispatcher:
    def __init__(self, workflow_id:str):
        self.workflow_id = workflow_id

    def dispatch_components_output_event(self, component_outputs: Dict[str, Union[ComponentModel, str]]):
        yield {
            "workflow_id": self.workflow_id,
            "outputs": component_outputs
        }

class QueuedEventDispatcher(EventDispatcher):
    def __init__(self, workflow_id: str, queue: asyncio.Queue):
        super().__init__(workflow_id)
        self._queue = queue

    def dispatch_components_output_event(self, component_outputs: Dict[str, Union[ComponentModel, str]]):
        event = {
            "workflow_id": self.workflow_id,
            "outputs": component_outputs
        }
        self._queue.put_nowait(event)
