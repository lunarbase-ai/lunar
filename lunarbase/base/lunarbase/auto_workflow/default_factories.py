# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import json

from langchain.prompts.prompt import PromptTemplate

from lunarbase.lunarbase.auto_workflow.config import (
    PROMPT_DATA_FILE,
    RELEVANT_INTENTS_PROMPT_TEMPLATE_FORMAT,
    RELEVANT_INTENTS_PROMPT_TEMPLATE,
    RELEVANT_COMPONENTS_PROMPT_TEMPLATE_FORMAT,
    RELEVANT_COMPONENTS_PROMPT_TEMPLATE,
    WORKFLOW_PROMPT_TEMPLATE_FORMAT,
    WORKFLOW_PROMPT_TEMPLATE,
    WORKFLOW_MODIFICATION_PROMPT_TEMPLATE_FORMAT,
    WORKFLOW_MODIFICATION_PROMPT_TEMPLATE,
    COMPONENT_PROMPT_TEMPLATE_FORMAT,
    COMPONENT_PROMPT_TEMPLATE,
)
from core.lunarcore.utils import get_file_content


def prompt_data_default():
    prompt_data = json.loads(get_file_content(PROMPT_DATA_FILE))
    return prompt_data


def relevant_intents_prompt_template_default():
    template = PromptTemplate.from_template(
        RELEVANT_INTENTS_PROMPT_TEMPLATE,
        template_format=RELEVANT_INTENTS_PROMPT_TEMPLATE_FORMAT,
    )
    return template


def relevant_components_prompt_template_default():
    template = PromptTemplate.from_template(
        RELEVANT_COMPONENTS_PROMPT_TEMPLATE,
        template_format=RELEVANT_COMPONENTS_PROMPT_TEMPLATE_FORMAT,
    )
    return template


def workflow_prompt_template_default():
    template = PromptTemplate.from_template(
        WORKFLOW_PROMPT_TEMPLATE, template_format=WORKFLOW_PROMPT_TEMPLATE_FORMAT
    )
    return template


def workflow_modification_prompt_template_default():
    template = PromptTemplate.from_template(
        WORKFLOW_MODIFICATION_PROMPT_TEMPLATE,
        template_format=WORKFLOW_MODIFICATION_PROMPT_TEMPLATE_FORMAT,
    )
    return template


def component_prompt_template_default():
    template = PromptTemplate.from_template(
        COMPONENT_PROMPT_TEMPLATE, template_format=COMPONENT_PROMPT_TEMPLATE_FORMAT
    )
    return template
