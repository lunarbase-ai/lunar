import logging
import os
import re
import torch

from dotenv import load_dotenv
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest
from transformers import AutoModelForCausalLM
from typing import Dict

from lunarcore.benchmark.auto_workflow.baseline_testers.config import (
    MIXTRAL_8X7B_LABEL,
    MIXTRAL_8X7B_DOTENV,
    MIXTRAL_8X7B_HF_ID,
    MIXTRAL_8X7B_TEMPERATURE,
    MIXTRAL_8X7B_TOP_P,
    MIXTRAL_8X7B_PYTHON_PATTERN,
    MAX_ANS_TOKENS,
)
from lunarcore.benchmark.auto_workflow.baseline_testers.baseline_tester import BaselineTester


class Mixtral_8x7B(BaselineTester):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(tester_name=MIXTRAL_8X7B_LABEL, logger=logger)
        load_dotenv(MIXTRAL_8X7B_DOTENV)
        self.token = os.environ["HUGGINGFACEHUB_API_TOKEN"]  # TODO: remove?
        self.python_pattern = re.compile(MIXTRAL_8X7B_PYTHON_PATTERN, re.DOTALL)


    def _llm_quest(self, template_variables: Dict):
        prompt = self._fill_prompt_template(template_variables)
        tokenizer = MistralTokenizer.v1()
        model = AutoModelForCausalLM.from_pretrained(MIXTRAL_8X7B_HF_ID, device_map="auto")
        completion_request = ChatCompletionRequest(messages=[UserMessage(content=prompt)])
        encoded_input = tokenizer.encode_chat_completion(completion_request).tokens
        input_ids = torch.tensor([encoded_input])
        attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
        with torch.no_grad():
            output = model.generate(
                input_ids.to('cuda'),
                attention_mask=attention_mask,
                max_length=MAX_ANS_TOKENS,
                temperature=MIXTRAL_8X7B_TEMPERATURE,
                top_p=MIXTRAL_8X7B_TOP_P,
                do_sample=True,
            )
        response = tokenizer.decode(output[0].tolist())
        input_text = tokenizer.decode(encoded_input)
        answer = response.replace(input_text, '')
        return answer


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

    tester = Mixtral_8x7B()
    output = tester.run_test('Test name', intent, files)
    print(output)