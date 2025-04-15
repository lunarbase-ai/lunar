// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { LLM, DataSourceType } from "@/models/llm/llm";
import api from "../api/lunarverse";

export const listLLMsAction = async (userId: string): Promise<LLM[]> => {
  const { data } = await api.get<LLM[]>(`/llm?user_id=${userId}`)
  return data
}

export const listLLMTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  const { data } = await api.get<DataSourceType[]>(`/llm/types?user_id=${userId}`)
  return data
}

export const createLLMAction = async (userId: string, llm: LLM): Promise<void> => {
  await api.post(`/llm?user_id=${userId}`, llm)
  return
}

export const editLLMAction = async (userId: string, llm: LLM): Promise<void> => {
  await api.put(`/llm?user_id=${userId}`, llm)
  return
}

export const deleteLLMAction = async (userId: string, llmId: string): Promise<void> => {
  await api.delete(`/llm/${llmId}?user_id=${userId}`)
  return
}
