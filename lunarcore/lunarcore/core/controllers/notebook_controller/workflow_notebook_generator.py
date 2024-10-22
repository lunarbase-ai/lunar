from collections import deque, defaultdict
from lunarcore.core.data_models import WorkflowModel, ComponentModel
from typing import List
import nbformat
from nbformat.notebooknode import NotebookNode
from lunarcore.utils import setup_logger
import re
import networkx as nx
from pydantic import BaseModel, Field

logger = setup_logger("notebook-generator")

class NotebookSetupModel(BaseModel):
    user_env_path: str = Field(None, description="The user environment file path")
    workflow_venv_path: str = Field(None, description="The workflow virtual environment path")
class WorkflowNotebookGenerator:
    def __init__(self):
        pass

    def generate(self, workflow: WorkflowModel, setup: NotebookSetupModel) -> NotebookNode:
        components: List[ComponentModel] = workflow.components_ordered()

        title_markdown_cell = self._generate_title_cell(workflow)
        env_setup_code_cell = self._generate_env_setup_cell(setup)
        component_imports_code_cell = self._generate_component_imports_cell(components)
        component_instances_code_cell = self._generate_component_instances_cell(components)
        orchestration_code_cells = self._generate_orchestration_cells(workflow)
        
        notebook = self._start_new_notebook()
        self._append_cells_to_notebook(notebook, [
            title_markdown_cell, 
            # env_setup_code_cell,
            component_imports_code_cell, 
            component_instances_code_cell,
            *orchestration_code_cells
        ])
        return notebook
    
    def _start_new_notebook(self) -> NotebookNode:
        return nbformat.v4.new_notebook()
    
    def _append_cells_to_notebook(self, notebook: NotebookNode, cells: List[NotebookNode]):
        return notebook.cells.extend(cells)

    def _generate_title_cell(self, workflow: WorkflowModel) -> NotebookNode:
        return nbformat.v4.new_markdown_cell(f"# {workflow.name}")
    
    def _generate_env_setup_cell(self, setup: NotebookSetupModel) -> NotebookNode:
        env_setup = f"from dotenv import load_dotenv\n\ndotenv_path = '{setup.user_env_path}'\nload_dotenv(dotenv_path)"
        return nbformat.v4.new_code_cell(env_setup)
    
    def _generate_component_imports_cell(self, components: List[ComponentModel]) -> NotebookNode:

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
    
    # @TODO: Refactor this method to make it more robust, easier to read, and propper handle the orchestration and all its cases. This is just a starting point. Its current implementation is not complete.
    def _generate_orchestration_cells(self, workflow: WorkflowModel) -> List[NotebookNode]:
        tasks = {comp.label: comp for comp in workflow.components}

        dag = workflow.get_dag()
        running_queue = deque(nx.topological_sort(dag))

        dependencies = self._group_dependencies_by_target_component(workflow.dependencies)

        orchestration_cells = []
        while len(running_queue) > 0:
            next_task = running_queue.popleft()
            task = tasks[next_task]

            instance_inputs = []

            input_dependencies = dependencies.get(task.label, [])
            for input in task.inputs:
                input_key = input.key
                input_value = input.value
                input_template_variables = input.template_variables

                if len(input_dependencies) > 0:
                    for dependency in input_dependencies:
                        if input_key == dependency.component_input_key:
                            if dependency.template_variable_key is not None and dependency.template_variable_key in input_template_variables:
                                
                                input_template_variables[dependency.template_variable_key] = f"{self._format_as_python_variable(dependency.source_label)}_result"
                                
                                mapped_template_variable = {key.split('.')[-1]: value for key, value in input_template_variables.items()}
                                input_value = input_value.format(**{key: f'{{{value}}}' for key, value in mapped_template_variable.items()})

                                input_value = f'f"{input_value}"'

                            else:
                                input_value = f"{self._format_as_python_variable(dependency.source_label)}_result"
                else:
                    input_value = f'"{input_value}"'

                instance_inputs.append(f"{input_key}={input_value}")

            instance_var_name = self._format_as_python_variable(task.label)
            instance_result_var_name = f"{instance_var_name}_result"

            run_call = f"{instance_result_var_name} = {instance_var_name}.run({', '.join(instance_inputs)})"

            orchestration_cells.append(nbformat.v4.new_code_cell(run_call))

        return orchestration_cells
    
    def _group_dependencies_by_target_component(self, dependencies):
        grouped_dependencies = defaultdict(list)
        for dependency in dependencies:
            grouped_dependencies[dependency.target_label].append(dependency)
        
        return dict(grouped_dependencies)
    