from lunarcore.core.data_models import WorkflowModel, ComponentModel
from typing import List
import nbformat
from nbformat.notebooknode import NotebookNode
from lunarcore.utils import setup_logger

logger = setup_logger("notebook-generator")

class NotebookGenerator:
    def __init__(self):
        pass

    def generate(self, workflow: WorkflowModel) -> NotebookNode:
        components: List[ComponentModel] = workflow.components_ordered()
        # tasks = {comp.label: comp for comp in workflow.components}
        # promises = {comp.label: dict() for comp in workflow.components}
        # dag = workflow.get_dag()
        # running_queue = deque(list(dag.nodes))
        # logger.info(f"Running queue: {running_queue}")
        notebook = self._start_new_notebook()


        title_markdown_cell = self._generate_title_cell(workflow)
        imports_code_cell = self._generate_imports_cell(components)

        notebook.cells.extend([title_markdown_cell, imports_code_cell])

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