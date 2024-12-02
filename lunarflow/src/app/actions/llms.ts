// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { LLM, DataSourceType } from "@/models/llm/llm";

export const listLLMsAction = async (userId: string): Promise<LLM[]> => {
  const openai: LLM = {
    id: "123456",
    name: "Azure OpenAI",
    connectionAttributes: {
      AZURE_DEPLOYMENT: 'lunar-chatgpt-4o',
      OPENAI_API_KEY: 'd8d1b0b5a5b94cc7a5fb12a49283fae3',
      AZURE_ENDPOINT: 'https://lunarchatgpt.openai.azure.com/',
      OPENAI_API_VERSION: '2024-02-01'
    },
    description: "open ai model description",
    type: "AZURE_OPENAI"
  }
  return [openai]
}

export const listLLMTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  const azureOpenAIType: DataSourceType = {
    id: "AZURE_OPEN_AI",
    name: "Azure Open AI",
    expectedConnectionAttributes: ['AZURE_DEPLOYMENT', 'OPENAI_API_KEY', 'AZURE_ENDPOINT', 'OPENAI_API_VERSION'],
  }
  return [azureOpenAIType]
}

export const createLLMAction = async (userId: string, llm: LLM): Promise<void> => {
  return
}

export const editLLMAction = async (userId: string, llm: LLM): Promise<void> => {
  return
}

export const deleteLLMAction = async (userId: string, llmId: string): Promise<void> => {
  return
}
