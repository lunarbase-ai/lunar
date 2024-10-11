from lunarcore.core.data_models import WorkflowModel, ComponentModel
from typing import List
import nbformat
from nbformat.notebooknode import NotebookNode
from lunarcore.utils import setup_logger
import json
import re

logger = setup_logger("notebook-generator")

class WorkflowNotebookGenerator:
    def __init__(self):
        pass

    def generate(self, workflow: WorkflowModel) -> NotebookNode:
        components: List[ComponentModel] = workflow.components_ordered()
        notebook = self._start_new_notebook()


        title_markdown_cell = self._generate_title_cell(workflow)
        imports_code_cell = self._generate_imports_cell(components)
        component_instances_code_cell = self._generate_component_instances_cell(components)


        # tasks = {comp.label: comp for comp in workflow.components}
        # promises = {comp.label: dict() for comp in workflow.components}

        # logger.info(f"Promises: {promises}")

        # logger.info(f"Input 2: {tasks['TEXTINPUT-2']}") 
        # logger.info("\n") 
        # logger.info(f"Input 1: {tasks['TEXTINPUT-1']}")  
        # logger.info("\n") 
        # logger.info(f"Input 1: {tasks['TEXTINPUT-0']}")  
        # dag = workflow.get_dag()say hi to {name}.
        # running_queue = deque(list(dag.nodes))

        
        notebook.cells.extend([
            title_markdown_cell, 
            imports_code_cell, 
            component_instances_code_cell
        ])

        return notebook
    
    def _start_new_notebook(self) -> NotebookNode:
        return nbformat.v4.new_notebook()

    def _generate_title_cell(self, workflow: WorkflowModel) -> NotebookNode:
        return nbformat.v4.new_markdown_cell(f"# {workflow.name}")
    
    def _generate_imports_cell(self, components: List[ComponentModel]) -> NotebookNode:

        import_statements = []

        for component in components:
            import_statement = component.get_component_import_path()

            if import_statement not in import_statements:
                import_statements.append(import_statement)

        return nbformat.v4.new_code_cell("\n".join(import_statements))
    
    def _generate_component_instances_cell(self, components: List[ComponentModel]) -> NotebookNode:
        component_instances = []
        for component in components:
            _component_class = component.get_component_class_name()

            var_name = self._format_as_python_variable(component.label)

            instance = f"{var_name} = {_component_class}()"

            component_instances.append(instance)

        return nbformat.v4.new_code_cell("\n".join(component_instances))
    
    def _format_as_python_variable(self, component_label: str) -> str:
        return re.sub(r'\W|^(?=\d)', '_', component_label).lower()