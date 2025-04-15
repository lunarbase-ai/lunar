// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { AxiosResponse } from "axios"
import api from "../api/lunarverse"

export const fetchFilesAction = async (workflowId: string, userId: string) => {
  const { data } = await api.get<string[]>(`/file/${workflowId}?user_id=${userId}`)
  return data
}

export const uploadFileAction = async (workflowId: string, formData: FormData, userId: string) => {
  const { data } = await api.post<any, AxiosResponse<string, any>>(`/file/${workflowId}/upload?user_id=${userId}`, formData)
  return data
}
