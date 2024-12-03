# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.auto_workflow import AutoWorkflow


PROTOCOL_FILE = 'protocol.txt'
PROTOCOL_TEMPLATE = """ANNOTATION PROTOCOL

This is a protocol for creating a test that generates a workflow, executes it with given inputs, and evaluates its output.

To create the test, please provide the following:
- A description of the workflow that is to be generated.
- A list of input files that are to be used as input to the workflow. The order does not matter. 
- A list of descriptions of the input files in the same order as the list of input files.
- A list of the expected outputs from the workflow (i.e. the expected outputs from all terminal components). Order does not matter.

Create a folder with all input files, and add a textfile to it with four lines according to the following example:
DESCRIPTION: 'A workflow where a local text file is uploaded and read, and then its content is outputted.'
INPUT FILES: 'text1.txt', 'pdf1.pdf'
FILE DESCIPTIONS: 'The text file to read', 'A PDF file that probably will not be used in this workflow'
OUTPUTS: 'This is the content of the text file.'

The workflow description may include any functionalities represented by the components given in the registry below, but can also include functionalities not represented. In that case, 'custom components' will be generated in the workflow.

Alternatively to providing the test folder, a test can be created instantly using the script at '/lunarcore.benchmark.auto_workflow/add_test.py'. Use the -h option to see how it works.


{components_str}

"""

asyncio.run(COMPONENT_REGISTRY.register(fetch=True))

component_registry = AutoWorkflow.components_str()
protocol_str = PROTOCOL_TEMPLATE.format(components_str=component_registry)

with open(PROTOCOL_FILE, 'w') as file:
    file.write(protocol_str)
