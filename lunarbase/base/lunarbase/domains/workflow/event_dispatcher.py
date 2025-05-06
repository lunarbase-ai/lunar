from typing import Dict

from lunarbase.modeling.data_models import ComponentModel


class EventDispatcher:
    def __init__(self, workflow_id:str):
        self.workflow_id = workflow_id

    def dispatch_components_output_event(self, component_outputs: Dict[str, ComponentModel]):
        yield {
            "workflow_id": self.workflow_id,
            "outputs": component_outputs
        }
