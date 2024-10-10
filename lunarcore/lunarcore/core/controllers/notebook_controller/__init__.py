from typing import Union, Dict
from lunarcore.config import LunarConfig
from lunarcore.utils import get_config
from lunarcore.core.persistence_layer import PersistenceLayer
from lunarcore.core.data_models import WorkflowModel

class NotebookController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self._persistence_layer = PersistenceLayer(config=self._config)

    async def save(self, workflow: WorkflowModel, user_id: str):
        workflow = WorkflowModel.model_validate(workflow)

        workflow_dag = workflow.get_dag()

        return {
            "workflow": workflow,
            "dag": workflow_dag,
        }