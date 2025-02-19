// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { Workflow } from "@/models/Workflow"
import api from "../api/lunarverse"

export const autoCreateWorkflowAction = async (intent: string, userId: string) => {
  const { data } = await api.post<Workflow>(`/auto_workflow?user_id=${userId}&intent=${intent}`)
  return data
}

export const autoEditWorkflowAction = async (workflow: Workflow, instruction: string, userId: string) => {
  const { data } = await api.post<Workflow>(`/auto_workflow_modification?user_id=${userId}&modification_instruction=${instruction}`, {
    ...workflow
  })
  return data
}
