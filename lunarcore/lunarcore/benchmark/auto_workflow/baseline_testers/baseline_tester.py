import io
import logging

from contextlib import redirect_stdout
from langchain.prompts.prompt import PromptTemplate
from typing import Dict, List

from lunarcore.core.typings.datatypes import File
from lunarcore.benchmark.auto_workflow.baseline_testers.config import (
    BASELINE_PROMPT_TEMPLATE,
    BASELINE_PROMPT_TEMPLATE_FORMAT,
    FILE_PROMPT_TEMPLATE,
)
from lunarcore.benchmark.auto_workflow.tester import Tester


class BaselineTester(Tester):
    def __init__(self, tester_name: str = None, logger: logging.Logger = None):
        super().__init__(tester_name, logger)
        self.prompt_template = PromptTemplate.from_template(
            BASELINE_PROMPT_TEMPLATE,
            template_format=BASELINE_PROMPT_TEMPLATE_FORMAT
        )

    def _llm_quest(self, template_variables: Dict):
        raise NotImplementedError("Subclass must implement abstract method")
    
    def _llm_ans_post_processing(self, llm_ans: str):
        raise NotImplementedError("Subclass must implement abstract method")
    
    def _fill_prompt_template(self, template_variables: Dict):
        return self.prompt_template.format(**template_variables)

    def _files2template_variable(self, files: List[File]):
        files_sb = []
        for file in files:
            file_prompt_repr = FILE_PROMPT_TEMPLATE.format(
                description=file.description,
                path=file.path,
            )
            files_sb.append(file_prompt_repr)
        return '\n'.join(files_sb)
    
    def _run_and_capture_output(self, code: str):
        output_stream = io.StringIO()
        with redirect_stdout(output_stream):
            exec(code)
        output = output_stream.getvalue()
        return output

    def run_test(self, test_name: str, intent: str, files: List[File]):
        self.logger.info(f"Starting test '{test_name}'")
        template_variables = {
            'task': intent,
            'files': self._files2template_variable(files)
        }
        self.logger.debug(f'Generating code for task: {intent}')
        llm_ans = self._llm_quest(template_variables)
        self.logger.debug(f'Got the following answer from LLM:\n{llm_ans}')
        code = self._llm_ans_post_processing(llm_ans)
        self.logger.debug(f'Post-processed LLM answer to the following:\n{code}')
        self.logger.debug(f'Running code...')
        code_output = self._run_and_capture_output(code).strip('\n')
        self.logger.debug(f'Got the following output:\n{code_output}')
        return [code_output]