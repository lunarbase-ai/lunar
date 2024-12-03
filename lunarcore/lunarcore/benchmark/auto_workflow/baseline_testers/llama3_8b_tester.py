import logging
import os
import re
import torch
import transformers

from dotenv import load_dotenv
from typing import Dict

from lunarcore.benchmark.auto_workflow.baseline_testers.config import (
    LLAMA3_8B_LABEL,
    LLAMA3_8B_DOTENV,
    LLAMA3_8B_HF_ID,
    LLAMA3_8B_TEMPERATURE,
    LLAMA3_8B_TOP_P,
    LLAMA3_8B_PYTHON_PATTERN,
    MAX_ANS_TOKENS,
)
from lunarcore.benchmark.auto_workflow.baseline_testers.baseline_tester import BaselineTester


class Llama3_8B(BaselineTester):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(tester_name=LLAMA3_8B_LABEL, logger=logger)
        load_dotenv(LLAMA3_8B_DOTENV)
        self.token = os.environ["HUGGINGFACEHUB_API_TOKEN"]
        self.python_pattern = re.compile(LLAMA3_8B_PYTHON_PATTERN, re.DOTALL)


    def _llm_quest(self, template_variables: Dict):
        prompt = self._fill_prompt_template(template_variables)

        pipeline = transformers.pipeline(
            "text-generation",
            model=LLAMA3_8B_HF_ID,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
            token=self.token
        )

        messages = [
            {"role": "system", "content": prompt},
        ]

        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = pipeline(
            messages,
            max_new_tokens=MAX_ANS_TOKENS,
            eos_token_id=terminators,
            do_sample=True,
            temperature=LLAMA3_8B_TEMPERATURE,
            top_p=LLAMA3_8B_TOP_P,
        )
        return outputs[0]["generated_text"][-1]['content']

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

    tester = Llama3_8B()
    output = tester.run_test('Test name', intent, files)
    print(output)