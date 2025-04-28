// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"
import api from "../api/lunarverse"
import { AxiosResponse } from "axios"

import { ComponentModel } from "@/models/component/ComponentModel"
import { Workflow, WorkflowReference } from "@/models/Workflow"

export const getWorkflowAction = async (id: string, userId: string) => {
  try {
    const { data } = await api.get<Workflow>(`/workflow/${id}?user_id=${userId}`)
    return data
  } catch (e) {
    console.error(e)
    throw e
  }
}

export const createWorkflowAction = async (name: string, description: string, userId: string) => {
  try {
    const { data } = await api.post<Workflow>(`/workflow?user_id=${userId}`, { name, description, userId: userId })
    return data
  } catch (e) {
    console.error(e)
    throw e
  }
}

export const createWorkflowFromTemplateAction = async (templateId: string, userId: string) => {
  try {
    const { data } = await api.post<Workflow>(`/workflow?user_id=${userId}&template_id=${templateId}`)
    return data
  } catch (e) {
    console.error(e)
    throw e
  }
}

export const saveWorkflowAction = async (workflow: Workflow, userId: string): Promise<void> => {
  try {
    await api.put(`/workflow?user_id=${userId}`, workflow)
    return
  } catch (e) {
    console.error(e)
    throw e
  }
}

export const runWorkflowAction = async (workflow: Workflow, userId: string) => {
  try {
    const { data } = await api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/workflow/run?user_id=${userId}`, workflow)
    return data
  } catch (e) {
    console.error(e)
  }
  return {}
}

export const cancelWorkflowAction = async (workflowId: string, userId: string) => {
  const { data } = await api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/workflow/${workflowId}/cancel?user_id=${userId}`)
  return data
}

export const generateWorkflowAction = async (workflow: Workflow, instruction: string, userId: string) => {
  const { data } = await api.post<Workflow>(`/auto_workflow_modification?user_id=${userId}&modification_instruction=${instruction}`, {
    workflow: workflow
  })
  return data
}

export const deleteWorkflowAction = async (workflowId: string, userId: string): Promise<void> => {
  await api.delete(`/workflow/${workflowId}?user_id=${userId}`)
}

export const listWorkflowsAction = async (userId: string) => {
  const { data } = await api.get<WorkflowReference[]>(`/workflow/short_list?user_id=${userId}`)
  return data
}

export const listWorkflowDemosAction = async (userId: string) => {
  const { data } = await api.get<WorkflowReference[]>(`/demo/list`)
  return data
}

export const createWorkflowFromComponentExampleAction = async (componentId: string, userId: string): Promise<Workflow> => {
  try {
    const { data } = await api.get<Workflow>(`/component/${componentId}/example?user_id=${userId}`)
    return data
  } catch (e) {
    console.error(e)
    throw e
  }
}

export const searchWorkflowAction = async (query: string, userId: string) => {
  //TODO: Move to a models file
  interface Option {
    id: string
    name: string
  }
  const { data } = await api.get<Option[]>(`/workflow/search?query=${query}&user_id=${userId}`)
  return data
}
