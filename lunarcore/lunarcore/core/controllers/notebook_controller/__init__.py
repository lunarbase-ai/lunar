from typing import Union, Dict, List
from lunarcore.config import LunarConfig, LUNAR_PACKAGE_NAME
from lunarcore.utils import get_config
from lunarcore.core.persistence_layer import PersistenceLayer
from lunarcore.core.data_models import WorkflowModel, ComponentModel
from lunarcore.utils import setup_logger
import nbformat
import os
from fastapi import UploadFile
from io import BytesIO

logger = setup_logger("notebook-controller")

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
        workflow_notebook_path = self._persistence_layer.get_user_workflow_notebook_path(
            workflow_id=workflow.id, user_id=user_id
        )

        nb = self._generate_notebook(workflow=workflow)
        
        file = UploadFile(
            filename="index.ipynb",
            file=BytesIO(nbformat.writes(nb).encode("utf-8"))
        )
        
        await self._persistence_layer.save_file_to_storage(
            workflow_notebook_path, file
        )
        
        return {
            "workflow": workflow,
            "dag": workflow.get_dag(),
            "ordered": workflow.components_ordered(),
        }

    def _generate_notebook(self, workflow: WorkflowModel):
        nb = nbformat.v4.new_notebook()

        components: List[ComponentModel] = workflow.components_ordered()

        title_cell = nbformat.v4.new_markdown_cell(f"# {workflow.name}")

        import_statements = self._generate_component_imports(components=components)
        imports_code_cell = nbformat.v4.new_code_cell(import_statements)

        nb.cells.extend([title_cell, imports_code_cell])

        return nb
        
    def _generate_component_imports(self, components: List[ComponentModel]) -> str:

        import_statements = []

        for component in components:
            component_path = component.get_component_code()
            component_class = component.get_component_class_name()

            parts = component_path.split(os.sep)
            
            try:
                index = parts.index(LUNAR_PACKAGE_NAME)
            except ValueError:
                raise ValueError(f"'{LUNAR_PACKAGE_NAME}' not found in the provided file path")
            
            relevant_parts = parts[index+1:]
            
            module_path = '.'.join(relevant_parts[:-1])
            
            import_statement = f"from {module_path} import {component_class}"

            if import_statement not in import_statements:
                import_statements.append(import_statement)                       

        return '\n'.join(import_statements)
    