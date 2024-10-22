from typing import Union, Dict
from lunarcore.config import LunarConfig, LUNAR_PACKAGE_NAME
from lunarcore.utils import get_config
from lunarcore.core.persistence import PersistenceLayer
from lunarcore.core.data_models import WorkflowModel
from lunarcore.utils import setup_logger
import nbformat
from fastapi import UploadFile
from io import BytesIO
from .workflow_notebook_generator import WorkflowNotebookGenerator, NotebookSetupModel
from pydantic import BaseModel, Field
import subprocess
from lunarcore.core.orchestration.process import PythonProcess

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

        user_env_path = self._persistence_layer.get_user_environment_path(user_id)
        workflow_venv_path = self._persistence_layer.get_workflow_venv(user_id, workflow.id)
        nb_setup = NotebookSetupModel(user_env_path=user_env_path, workflow_venv_path=workflow_venv_path)
        
        nb = self._notebook_generator.generate(
            workflow, nb_setup
        )
        
        file = UploadFile(
            filename="index.ipynb",
            file=BytesIO(nbformat.writes(nb).encode("utf-8"))
        )

        workflow_notebook_path = self._persistence_layer.get_user_workflow_notebook_path(
            workflow_id=workflow.id, user_id=user_id
        )
        
        await self._persistence_layer.save_file_to_storage(
            workflow_notebook_path, file
        )
        
        return {
            "workflow": workflow,
            "dag": workflow.get_dag(),
            "ordered": workflow.components_ordered(),
        }
    
    async def open(self, workflow: WorkflowModel, user_id: str, jupyterConfig: "JupyterServerConfigModel"):
        jupyterConfig = JupyterServerConfigModel(**jupyterConfig)

        logger.info(workflow.id)

        nb_path = self._persistence_layer.get_user_workflow_notebook_path(
            workflow_id=workflow.id, user_id=user_id
        )
        nb_exists = await self._persistence_layer.file_exists(f"{nb_path}index.ipynb")

        if not nb_exists:
            await self.save(workflow, user_id)

        workflow_venv_path = self._persistence_layer.get_workflow_venv(workflow.id, user_id)

        activate_script = f"{workflow_venv_path}/bin/activate"
        python_executable = f"{workflow_venv_path}/bin/python"

        core_sys_paths = PythonProcess.get_core_info().get('locations', [])
        p_path = ":".join(core_sys_paths + [python_executable])
        if p_path.endswith(":"):
            p_path = p_path.rstrip(":")

        jupyter_path = f"{workflow_venv_path}/share/jupyter"
        
        command = [
            "bash", "-c", 
            f"source {activate_script} && export PYTHONPATH={p_path} && {python_executable} -m ipykernel install --prefix '{workflow_venv_path}' --name '{workflow.id}' --display-name '{workflow.name}' && export JUPYTER_PATH={jupyter_path} && jupyter lab --config='{nb_path}/.jupyter_lab_config.py' --ip={jupyterConfig.host} --port={jupyterConfig.port}"
        ]
        
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output and error (if any)
        print(result.stdout)
        print(result.stderr)

class JupyterServerConfigModel(BaseModel):
    host: str = Field("localhost", description="The host of the Jupyter server")
    port: int = Field(8888, description="The port of the Jupyter server")
    notebook_dir: str = Field("", description="The root directory of the Jupyter server")
    allow_unauthenticated_access: bool = Field(True, description="Whether the Jupyter server should allow unauthenticated access")
    token: str = Field("", description="The token to access the Jupyter server")
    password: str = Field("", description="The password to access the Jupyter server")
    default_kernel_name: str = Field(None, description="The default kernel name of the Jupyter server")