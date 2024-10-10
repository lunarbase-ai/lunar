from typing import Union, Dict
from lunarcore.config import LunarConfig
from lunarcore.utils import get_config
from lunarcore.core.persistence_layer import PersistenceLayer
from lunarcore.core.data_models import WorkflowModel
from lunarcore.utils import setup_logger

from lunarcore.core.controllers.notebook_controller.services.notebook_generator import WorkflowNotebookGenerator

import nbformat

logger = setup_logger("notebook-controller")

class NotebookController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self._persistence_layer = PersistenceLayer(config=self._config)
        self._notebook_generator = WorkflowNotebookGenerator()

    async def save(self, workflow: WorkflowModel, user_id: str):
        workflow = WorkflowModel.model_validate(workflow)
        workflow_notebook_path = self._persistence_layer.get_user_workflow_notebook_path(
            workflow_id=workflow.id, user_id=user_id
        )
        # workflow_dag = workflow.get_dag()
        # workflow_venv_dir = self._persistence_layer.get_workflow_venv(
        #     user_id=user_id, workflow_id=workflow.id
        # )
        # workflow_path = self._persistence_layer.get_user_workflow_path(
        #         workflow_id=workflow.id, user_id=user_id
        #     )
        # user_env_path = self._persistence_layer.get_user_environment_path(user_id)

        nb = self._notebook_generator.generate(workflow=workflow)

        with open(f"{workflow_notebook_path}/index.ipynb", "w") as f:
            nbformat.write(nb, f)
        
        return {
            "workflow": workflow,
        }

        