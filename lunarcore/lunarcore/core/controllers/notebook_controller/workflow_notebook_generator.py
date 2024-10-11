from collections import deque
from lunarcore.core.data_models import WorkflowModel, ComponentModel
from typing import List
import nbformat
from nbformat.notebooknode import NotebookNode
from lunarcore.utils import setup_logger
import json
import re
import networkx as nx

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
        orchestration_cells = self._generate_orchestration_cells(workflow)
        output_cell = self._generate_output_cell(components)
        
        notebook.cells.extend([
            title_markdown_cell, 
            imports_code_cell, 
            component_instances_code_cell,
            *orchestration_cells,
            output_cell
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
    
    # @TODO: Refactor this method to make it more robust and propper handle the orchestration. This is just a starting point. Its current implementation is not complete.
    def _generate_orchestration_cells(self, workflow: WorkflowModel) -> List[NotebookNode]:
        tasks = {comp.label: comp for comp in workflow.components}

        dag = workflow.get_dag()
        running_queue = deque(nx.topological_sort(dag))

        dependencies = workflow.dependencies

        orchestration_cells = []
        while len(running_queue) > 0:
            next_task = running_queue.popleft()
            task = tasks[next_task]

            instance_var_name = self._format_as_python_variable(task.label)
            instance_result_var_name = f"{instance_var_name}_result"

            component_inputs = []

            input_dependencies = self._get_component_input_dependencies(dependencies, task.label)
            for input in task.inputs:
                key = input.key
                value = input.value
                template_variables = input.template_variables

                if len(input_dependencies) > 0:
                    for dependency in input_dependencies:
                        if key == dependency.component_input_key:
                            if dependency.template_variable_key is not None and dependency.template_variable_key in template_variables:
                                template_variables[dependency.template_variable_key] = f"{self._format_as_python_variable(dependency.source_label)}_result"
                                mapped_variables = {key.split('.')[-1]: value for key, value in template_variables.items()}
                                value = value.format(**{key: f'{{{value}}}' for key, value in mapped_variables.items()})
                                value = f'f"{value}"'

                            else:
                                value = f"{self._format_as_python_variable(dependency.source_label)}_result"
                else:
                    value = f'"{value}"'

                component_inputs.append(f"{key}={value}")

            run_call = f"{instance_result_var_name} = {instance_var_name}.run({', '.join(component_inputs)})"

            orchestration_cells.append(nbformat.v4.new_code_cell(run_call))

        return orchestration_cells
    
    def _get_component_input_dependencies(self, dependencies, task_label):
        input_dependencies = []
        for dependency in dependencies:
            target_label = dependency.target_label
            if target_label == task_label:
                input_dependencies.append(dependency)
                
        return input_dependencies
    
    def _generate_output_cell(self, components: List[ComponentModel]) -> NotebookNode:
        last_component = components[-1]
        var_name = self._format_as_python_variable(last_component.label)

        return nbformat.v4.new_code_cell(f"print({var_name}_result)")