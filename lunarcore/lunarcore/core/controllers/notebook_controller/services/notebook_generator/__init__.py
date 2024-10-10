from lunarcore.core.data_models import WorkflowModel
import nbformat

class WorkflowNotebookGenerator():
    def __init__(self):
        pass

    def generate(self, workflow: WorkflowModel):
        # Step 1: Create a new notebook object
        nb = nbformat.v4.new_notebook()

        # Step 2: Create cells
        code_cell = nbformat.v4.new_code_cell("print('Hello, Jupyter 3!')")
        markdown_cell = nbformat.v4.new_markdown_cell("# This is a markdown cell")

        # Step 3: Add cells to the notebook
        nb.cells.extend([code_cell, markdown_cell])

        return nb