import logging
import os
import re
import torch
import transformers

from dotenv import load_dotenv
from typing import Dict

from lunarcore.benchmark.auto_workflow.baseline_testers.config import (
    GEMMA2_9B_LABEL,
    GEMMA2_9B_DOTENV,
    GEMMA2_9B_HF_ID,
    GEMMA2_9B_TEMPERATURE,
    GEMMA2_9B_TOP_P,
    GEMMA2_9B_PYTHON_PATTERN,
    MAX_ANS_TOKENS,
)
from lunarcore.benchmark.auto_workflow.baseline_testers.baseline_tester import BaselineTester


class Gemma2_9B(BaselineTester):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(tester_name=GEMMA2_9B_LABEL, logger=logger)
        load_dotenv(GEMMA2_9B_DOTENV)
        self.token = os.environ["HUGGINGFACEHUB_API_TOKEN"]
        self.python_pattern = re.compile(GEMMA2_9B_PYTHON_PATTERN, re.DOTALL)


    def _llm_quest(self, template_variables: Dict):
        prompt = self._fill_prompt_template(template_variables)

        pipe = transformers.pipeline(
            "text-generation",
            model=GEMMA2_9B_HF_ID,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device="cuda",  # replace with "mps" to run on a Mac device
            token=self.token,
        )

        messages = [
            {"role": "user", "content": prompt},
        ]

        outputs = pipe(
            messages,
            max_new_tokens=MAX_ANS_TOKENS,
            do_sample=True,
            temperature=GEMMA2_9B_TEMPERATURE,
            top_p=GEMMA2_9B_TOP_P,
        )
        
        llm_ans = outputs[0]["generated_text"][-1]["content"].strip()
        return llm_ans

    def _llm_ans_post_processing(self, llm_ans: str):
        # TODO: fix (misses eg. ```python...```), for now temporary solution below
        # match = self.python_pattern.search(llm_ans)
        # if match:
        #     llm_ans = match.group(1)#.strip()
        if '```' in llm_ans:
            start_index = llm_ans.index('```')
            llm_ans = llm_ans[start_index:]
            code_index = llm_ans.index('\n') + 1
            llm_ans = llm_ans[code_index:]
            if '```' in llm_ans:
                end_index = llm_ans.rindex('```')
                llm_ans = llm_ans[:end_index]
        return llm_ans


if __name__ == '__main__':
    from lunarcore.core.typings.datatypes import File
    example_text_file_path = os.path.join(os.path.dirname(__file__), 'test', 'test_text_file.txt')
    files = [
        File(
            path=example_text_file_path,
            description='A textfile',
        )
    ]

    intent = 'Output the content of a file.'

    tester = Gemma2_9B()
    output = tester.run_test('Test name', intent, files)
    print(output)