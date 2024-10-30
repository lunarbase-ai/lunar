# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase


from typing import Union, Dict

from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from lunarbase.config import LunarConfig
from langchain.prompts.prompt import PromptTemplate

CODE_COMPLETION_TEMPLATE = """
You are a code copilot.
When considering the given code, please note that it might contain comments starting with ## as instructions for you.
Follow these instructions to help the code work properly.
Simple comments that start with a single # are just normal comments.
Output only the resulting code and the previously existing comments.
The code's output should be the content of the 'result' variable.
You cannot use external libraries.

CODE: {code}
"""


class CodeCompletionController:
    def __init__(
        self,
        config: Union[str, Dict, LunarConfig],
    ):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

    def complete(self, code: str):
        client = AzureChatOpenAI(
            openai_api_version=self._config.get("OPENAI_API_VERSION", None),
            deployment_name=self._config.get("AZURE_DEPLOYMENT", None),
            openai_api_key=self._config.get("OPENAI_API_KEY", None),
            azure_endpoint=self._config.get("AZURE_ENDPOINT", None),
            temperature=0.7,
        )
        prompt_template = PromptTemplate(
            input_variables=["code"],
            template=CODE_COMPLETION_TEMPLATE,
        )

        result = client(
            [HumanMessage(content=prompt_template.format(code=code))]
        ).content

        str(result).strip("\n").strip()
