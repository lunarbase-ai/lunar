# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import os

from lunarcore.config import GLOBAL_CONFIG

# Regex patterns
PATTERN_JSON = r"{(?:[^{}]|(?R))*}"  # Note: assumes JSON starts with {}
PATTERN_DEF_FUNC = r"(\s*def\s+\w+\s*\(.*?\))(\s*->\s*\w+)*(\s*:)"  # \g<1> == `def f(...)`  \g<2> == `-> str`  \g<3> == `:`
PATTERN_DEF_TYPES = r":\s*\[*\w+\]*\s*"  # Designed for `: ComponentInput` and `[ComponentInput]` -- fails on eg. `Union[ComponentInput, List[ComponentInput]]`
PATTERN_LLM_ANS_PYTHON = pattern = r"```python\n(.*)```"

# Azure OpenAI API parameters
OPENAI_MODEL_NAME = "gpt-4o"
OPENAI_TEMPERATURE = 1e-16
OPENAI_API_TYPE = "azure"
OPENAI_API_VERSION = "2024-02-01"
OPENAI_TOP_P = 1e-16
OPENAI_SEED = 1234
OPENAI_MODEL_KWARGS = {"top_p": OPENAI_TOP_P, "seed": OPENAI_SEED}

# OpenAI environmental variables
OPENAI_API_KEY_ENV = GLOBAL_CONFIG.OPENAI_API_KEY
AZURE_ENDPOINT_ENV = GLOBAL_CONFIG.AZURE_ENDPOINT
OPENAI_DEPLOYMENT_NAME = GLOBAL_CONFIG.AZURE_DEPLOYMENT

# Paths
PROMPT_DATA_FILE = os.path.join(os.path.dirname(__file__), "prompt_data.json")
EXAMPLE_WORKFLOWS_DIR = "example_workflows"

# Placeholder for input values that the user needs to fill in
EXAMPLES_USER_INPUT = ":undef:"

# Format of template variable label
TEMPLATE_VARIABLE_KEY_PREFIX = "{label}."
TEMPLATE_VARIABLE_KEY_TEMPLATE = "{label}.{variable}"

# Representation of components (eg COMPONENT1, COMPONENT2, ...)
COMPONENT_LABEL_PREFIX = "COMPONENT"

# Pattern of invalid sources like [COMPONENT1.preview]
MISSED_PROPERTY_GETTER_PATTERN = r"(\[(COMPONENT\d+).([a-zA-Z0-9._]+)\])"

# Prompt representation of input from another component
COMPONENT_SOURCE_REPR = "[{label}]"
TEMPLATE_VARIABLE_REPR = "{{{template_variable}}}"

# Common prompt templates
PROMPT_FILE_TEMPLATE = "{description}: {path}"
PROMPT_NO_FILES_REPR = "-"

# LlamaIndex
INDEX_TYPE = "summary"
INDEX_ROOT_DIR = os.path.join(
    os.path.dirname(__file__),
    "llamaindex_persist",
)
INDEX_PATH = os.path.join(
    INDEX_ROOT_DIR,
    f"components_index",
)
INDEX_JSON_PATH = os.path.join(INDEX_ROOT_DIR, "components.json")
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
EMBEDDING_DEPLOYMENT_NAME = "lunar-embeddings"

# Upper limmits of examples in prompt string
MAX_NR_EXAMPLES = 15
MAX_NR_EXTRA_EXAMPLES = 4
NR_INTENT_EXAMPLES = 2


#################################################
#### Prompt template for generating workflow ####
#################################################

WORKFLOW_PROMPT_TEMPLATE_FORMAT = "jinja2"
WORKFLOW_PROMPT_TEMPLATE = """
{{components}}

You are an assistent composing components to solve tasks.
Given the components above, select the most relevant components to solve the task below.
If needed, you can also use components not present in the component registry above. In that case, also provide a short component description that can be used to generate the component implementation with an LLM chat bot.
The resulting composition will be a graph (called "workflow") of connected components that are to be run together to output some result.
Make sure that input/output matches for each connection in the workflow.
Let each component in the workflow get some unique ID (eg. "COMPONENT1", "COMPONENT2", etc).
Output the workflow on JSON format according to the examples below.
Output only the JSON data.

{{examples}}

TASK:
{{task}}
AVAILABLE FILES:
{{files}}
"""
WORKFLOW_PROMPT_EXAMPLE_TEMPLATE = """
Here is an example workflow:
Task:
{description}
Available files:
{files}
Workflow:
{workflow_llm_repr}
"""


###########################################################
#### Prompt template for generating a custom component ####
###########################################################

COMPONENT_PROMPT_TEMPLATE_FORMAT = "jinja2"
COMPONENT_RUN_DEF = "def run(self, inputs, **kwargs):"
COMPONENT_INPUTS_POSTPROCESS = "inputs = {input_component.key: input_component for input_component in (inputs if type(inputs) is list else [inputs])}"
COMPONENT_PROMPT_TEMPLATE = """
You are a programmer.
Write a Python program according to the program description and the program inputs below.
Structure and format the code in the same way as in the examples below.
The code must contain a method `{run_def}`. This is the method that will be called to run the code.
The first line of the run method must be: `{inputs_postprocess}`
Output only the resulting Python code.

{{{{examples}}}}

DESCRIPTION: {{{{description}}}}
INPUT LABELS: {{{{input_labels}}}}
""".format(
    run_def=COMPONENT_RUN_DEF, inputs_postprocess=COMPONENT_INPUTS_POSTPROCESS
)
COMPONENT_PROMPT_EXAMPLE_TEMPLATE = """
Here is an example:
Description of the program:
{description}
Input labels:
{input_labels}
Implementation:
{code}
"""


#################################################
#### Prompt template for modifying workflow #####
#################################################

WORKFLOW_MODIFICATION_PROMPT_TEMPLATE_FORMAT = "jinja2"
WORKFLOW_MODIFICATION_PROMPT_TEMPLATE = """
{{components}}

You are an assistent composing components to solve tasks.
The composition of components (called "workflow") is a graph of connected components that are to be run together to output some result.
You will be given a workflow and an instruction on how to modify it.
Add or remove components in the workflow according to the instruction.
You can add components from the component registry above.
If needed, you can also add components not present in the component registry above. In that case, also provide a short component description that can be used to generate the component implementation with an LLM chat bot.
Make sure that input/output matches for each connection in the workflow.
Let each component in the workflow get some unique ID (eg. "COMPONENT1", "COMPONENT2", etc).
Output the modified workflow on JSON format according to the examples below.
Output only the JSON data.

{{workflow_examples}}

{{modification_examples}}


INSTRUCTION: {{instruction}}
WORKFLOW: {{workflow}}
"""
WORKFLOW_MODIFICATION_PROMPT_WORKFLOW_EXAMPLE_TEMPLATE = """
Here is an example workflow with the description {description}:
{workflow_llm_repr}
"""
WORKFLOW_MODIFICATION_PROMPT_EXAMPLE_TEMPLATE = """
Here is an example answer for modifying a workflow according to an instruction:
Instruction:
{task}
Workflow:
{initial_workflow_llm_repr}
Answer:
{answer_workflow_llm_repr}
"""


#########################################################
#### Prompt for picking relevant examples by intent #####
#########################################################
RELEVANT_INTENTS_PROMPT_TEMPLATE_FORMAT = "jinja2"
RELEVANT_INTENTS_PROMPT_TEMPLATE = """
You are an assistant creating few-shot prompts to an LLM.
The prompt will be used to create a workflow (a computer program consisting of composed program components) that solves a task.
Your task is to choose which examples (shots) to use in the few-shot prompt to the LLM.
Choose the {{nr_relevant_intent_examples}} most relevant example tasks/descriptions for the task/description below.
Output each chosen example task/description on a separate line according to the examples below.
Use exactly the same formulation and characters for the chosen example tasks/descriptions as in the list with given list of example tasks/descriptions.
Sort by relevance (the most relevant task/description first).
Output only the list.

Here is an example:
Example tasks/descriptions to choose 2 tasks/descriptions from:
A workflow for uploading a local .tex file, then compiling the LaTeX file to a PDF file, and finally compressing it to a ZIP file.
A workflow for uploading a PDF file and extracting its content. Then retrieve the contents of the results section, and create a report about it
A workflow that takes the path of a local text file as input, reads the file and outputs its content as a string. Then, search for the substring 'abc' in this string. Output 'Yes' if present, otherwise 'No'.
Extracts a zipped PDF file, reads the PDF file and summarizes the text content using an LLM.
Reads a PDF file and outputs two things: a summary of the text content (using an LLM) and a report with the whole text content.
A workflow reading a file and creating a report of the content.
Extracts a mathematical expression from an image and evaluates it.
Reads a JSON file containing a list of URLs. Outputs a list on Python format of the status codes when requesting each URL.
Reads two PDFs and outputs the content of the one with shortest text.
Reads a file and performs NER on it. Then extracts all found persons.
Task/description:
Create a workflow that takes two ZIP files as input, extracts them, and outputs the ZIP file name of the one with most files.
Answer:
Extracts a zipped PDF file, reads the PDF file and summarizes the text content using an LLM.
Reads two PDFs and outputs the content of the one with shortest text.

EXAMPLE TASKS/DESCRIPTIONS TO CHOOSE {{nr_relevant_intent_examples}} TASKS/DESCRIPTIONS FROM:
{{example_intents}}
TASK/DESCRIPTION:
{{intent}}
"""


#################################################
#### Prompt for picking relevant components #####
#################################################
RELEVANT_COMPONENTS_PROMPT_TEMPLATE_FORMAT = "jinja2"
RELEVANT_COMPONENTS_PROMPT_TEMPLATE = """
{{components}}

You are an assistent composing components to solve tasks.
The composition of components (called "workflow") is a graph of connected components that are to be run together to output some result.
You will be given a description of a workflow to be created.
Your task is to select the most relevant components for the workflow.
Output your selected components on one comma-space-separated line according to the examples below.
The list should be ordered after relevance of the components.
Output only the list.


{{examples}}


DESCRIPTION: {{description}}
"""
RELEVANT_COMPONENTS_EXAMPLE_TEMPLATE = """
Here is an example of relevant components for a workflow description:
Description:
{description}
Answer:
{answer}
"""
