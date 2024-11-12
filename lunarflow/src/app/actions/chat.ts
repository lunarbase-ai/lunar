// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { getUserId } from "@/utils/getUserId"
import { AxiosResponse } from "axios"
import api from "../api/lunarverse"
import { ChatResponse } from "@/models/chat/chat"

export const sendMessageAction = async (message: string, workflowIds: string[]) => {
  const user = await getUserId()
  const { data } = await api.post<any, AxiosResponse<ChatResponse, any>>(`/chat/generate?user_id=${user}`, {
    messages: [{ type: 'human', content: message }],
    workflows: workflowIds
  })
  return data
}