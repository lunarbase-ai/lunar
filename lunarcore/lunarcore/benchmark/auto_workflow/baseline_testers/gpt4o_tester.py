import logging
import os
import re

from langchain_openai import AzureChatOpenAI
from typing import Dict

from lunarcore.benchmark.auto_workflow.baseline_testers.config import (
    DOTENV_PATH,
    GPT4O_LABEL,
    GPT4O_OPENAI_API_KEY_ENV,
    GPT4O_AZURE_ENDPOINT_ENV,
    GPT4O_MODEL_NAME,
    GPT4O_TEMPERATURE,
    GPT4O_API_TYPE,
    GPT4O_API_VERSION,
    GPT4O_DEPLOYMENT_NAME,
    GPT4O_MODEL_KWARGS,
    GPT4O_PYTHON_PATTERN,
)
from lunarcore.benchmark.auto_workflow.baseline_testers.baseline_tester import BaselineTester


class GPT4oTester(BaselineTester):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(tester_name=GPT4O_LABEL, logger=logger)
        self.client = self._create_client()
        self.python_pattern = re.compile(GPT4O_PYTHON_PATTERN, re.DOTALL)

    def _create_client(self):
        client = AzureChatOpenAI(
            model_name=GPT4O_MODEL_NAME,
            temperature=GPT4O_TEMPERATURE,
            openai_api_type=GPT4O_API_TYPE,
            openai_api_version=GPT4O_API_VERSION,
            deployment_name=GPT4O_DEPLOYMENT_NAME,
            openai_api_key=os.environ.get(GPT4O_OPENAI_API_KEY_ENV, ''),
            azure_endpoint=os.environ.get(GPT4O_AZURE_ENDPOINT_ENV, ''),
            model_kwargs=GPT4O_MODEL_KWARGS,
        )
        return client
    
    def _llm_quest(self, template_variables: Dict):
        chain = self.prompt_template | self.client
        chain_results = chain.invoke(template_variables)
        result_text = chain_results.content
        return result_text

    def _llm_ans_post_processing(self, llm_ans: str):
        match = self.python_pattern.search(llm_ans)
        if match:
            llm_ans = match.group(1)#.strip()
        return llm_ans


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(DOTENV_PATH)

    from lunarcore.core.typings.datatypes import File
    example_text_file_path = os.path.join(os.path.dirname(__file__), 'test', 'test_text_file.txt')
    files = [
        File(
            path=example_text_file_path,
            description='A textfile',
        )
    ]

    intent = 'Output the content of a file.'

    tester = GPT4oTester()
    output = tester.run_test(intent, files)
    print(output)