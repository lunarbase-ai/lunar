from pydantic import BaseModel, Field
import subprocess
from lunarcore.core.orchestration.process import PythonProcess
import os
import json
from dotenv import dotenv_values

class JupyterServerManager:
    def __init__(self: "JupyterServerManager", config: "JupyterServerConfigModel"):
        self._config = config

    def create_config_file(self):
        config_content = f"c = get_config() # type: ignore\nc.ServerApp.ip = '{self._config.host}'\nc.ServerApp.port = {self._config.port}\nc.ServerApp\nc.ServerApp.notebook_dir = '{self._config.notebook_path}'\nc.ServerApp.allow_unauthenticated_access = {self._config.allow_unauthenticated_access}\nc.NotebookApp.token = '{self._config.token}'\nc.NotebookApp.password = '{self._config.password}'\nc.MultiKernelManager.default_kernel_name = '{self._config.kernel_name}'"

        with open(self._config.jupyter_config_path, 'w') as config_file:
            config_file.write(config_content)

    def create_kernel(self):
        kernel_dir = self._config.jupyter_share_path + f"/kernels/{self._config.kernel_name}"
        
        os.makedirs(kernel_dir, exist_ok=True)
        
        data = {
            "argv": [
                self._config.python_executable_path,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}"
            ],
            "display_name": self._config.kernel_display_name,
            "language": "python",
            "metadata": {
                "debugger": True
            },
            "env": dotenv_values(self._config.user_dotenv_path)
        }

        kernel_json_path = os.path.join(kernel_dir, "kernel.json")
        with open(kernel_json_path, 'w') as kernel_file:
            json.dump(data, kernel_file, indent=4)

    def run(self):
        command = [
            "bash", "-c", 
            f"source {self._config.venv_activate_script_path} && export PYTHONPATH={self._config.python_shared_environ_path} && export JUPYTER_PATH={self._config.jupyter_share_path} && jupyter lab --config='{self._config.jupyter_config_path}'"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)

        print(result.stdout)
        print(result.stderr)


class JupyterServerConfigModel(BaseModel):
    host: str = Field("localhost", description="The host of the Jupyter server")
    port: int = Field(8888, description="The port of the Jupyter server")
    notebook_path: str = Field(description="The root directory of the Jupyter server")
    allow_unauthenticated_access: bool = Field(True, description="Whether the Jupyter server should allow unauthenticated access")
    token: str = Field("", description="The token to access the Jupyter server")
    password: str = Field("", description="The password to access the Jupyter server")
    kernel_name: str = Field(description="The default kernel name of the Jupyter server")
    kernel_display_name: str = Field(description="The default kernel display name of the Jupyter server")
    user_dotenv_path: str = Field(description="The path to the user environment file")
    workflow_venv_path: str = Field(description="The path to the virtual environment of the workflow")

    @property
    def jupyter_config_path(self):
        """
        Path to the Jupyter Lab configuration file.
        """
        return f"{self.notebook_path}/.jupyter_lab_config.py"
    
    @property
    def jupyter_share_path(self):
        """
        Path to the Jupyter Lab share directory.
        """
        return f"{self.workflow_venv_path}/share/jupyter"
    
    @property
    def python_executable_path(self):
        """
        Path to the Python executable in the workflow virtual environment.
        """
        return f"{self.workflow_venv_path}/bin/python"
    
    @property
    def venv_activate_script_path(self):
        """
        Path to the virtual environment activation script.
        """
        return f"{self.workflow_venv_path}/bin/activate"
    
    @property
    def python_shared_environ_path(self):
        """
        Path to the Python environment shared by the workflow and lunarcore.
        """
        core_sys_paths = PythonProcess.get_core_info().get('locations', [])
        p_path = ":".join(core_sys_paths + [self.python_executable_path])
        if p_path.endswith(":"):
            p_path = p_path.rstrip(":")

        return p_path