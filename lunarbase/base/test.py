#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import re
from typing import List

RUN_OUTPUT_START = "<COMPONENT OUTPUT START>"
RUN_OUTPUT_END = "<COMPONENT OUTPUT END>"

WORKFLOW_OUTPUT_START = "<WORKFLOW OUTPUT START>"
WORKFLOW_OUTPUT_END = "<WORKFLOW OUTPUT END>"

if __name__ == "__main__":

    input = [
        '<COMPONENT OUTPUT START>\n{"id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0", "workflow_id": "2c933fe0-3df9-408d-aa97-cc4a477fe656", "name": "Python coder", "class_name": "PythonCoder", "description": "Performs customized Python code execution. Outputs the value that the Python variable `result` is set to during the execution of the Python code.\\nInputs:\\n  `Code` (str): A string of the Python code to execute.  If needed, the Python code can be inputted manually by the user.\\nOutput (Any): The value of the variable `result` in the Python code after execution.", "group": "Coders", "inputs": [{"id": "346dce6e-3807-467f-b2e5-4f9629da4e49", "key": "code", "data_type": "CODE", "value": "import time\\nresult = \\"Hello\\"\\ntime.sleep(2)", "template_variables": {}, "component_id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0"}], "output": {"data_type": "ANY", "value": "Hello", "component_id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0"}, "label": "PYTHONCODER-0", "configuration": {"force_run": false}, "version": null, "is_custom": false, "is_terminal": false, "position": {"x": 0.0, "y": 0.0}, "timeout": 600, "component_code": null, "component_code_requirements": null, "component_example_path": "/Users/danilomirandagusicuma/lunarbase/persistence/system/component_library/examples/python_coder.json", "invalid_errors": []}\n<COMPONENT OUTPUT END>', '<COMPONENT OUTPUT START>\n{"id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0", "workflow_id": "2c933fe0-3df9-408d-aa97-cc4a477fe656", "name": "Python coder", "class_name": "PythonCoder", "description": "Performs customized Python code execution. Outputs the value that the Python variable `result` is set to during the execution of the Python code.\\nInputs:\\n  `Code` (str): A string of the Python code to execute.  If needed, the Python code can be inputted manually by the user.\\nOutput (Any): The value of the variable `result` in the Python code after execution.", "group": "Coders", "inputs": [{"id": "346dce6e-3807-467f-b2e5-4f9629da4e49", "key": "code", "data_type": "CODE", "value": "import time\\nresult = \\"{hello}, Goodbye!\\"\\ntime.sleep(2)", "template_variables": {"code.hello": "Hello"}, "component_id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0"}], "output": {"data_type": "ANY", "value": "Hello, Goodbye!", "component_id": "d70a7641-1f63-47e6-aaf0-83fac698e5c0"}, "label": "PYTHONCODER-1", "configuration": {"force_run": false}, "version": null, "is_custom": false, "is_terminal": true, "position": {"x": 0.0, "y": 0.0}, "timeout": 600, "component_code": null, "component_code_requirements": null, "component_example_path": "/Users/danilomirandagusicuma/lunarbase/persistence/system/component_library/examples/python_coder.json", "invalid_errors": []}\n<COMPONENT OUTPUT END>'
    ]

    def parse_component_result(result: List):
        expected_output = None
        for out in result:
            if RUN_OUTPUT_START in out and RUN_OUTPUT_END in out:
                pattern = re.compile('<COMPONENT OUTPUT START>(.*?)<COMPONENT OUTPUT END>', re.DOTALL)
                match = re.search(pattern, out)
                try:
                    expected_output = match.group(1)
                except IndexError:
                    continue
                break
        return expected_output

    print(parse_component_result(input))

