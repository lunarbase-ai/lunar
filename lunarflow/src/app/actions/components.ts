// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { ComponentModel } from "@/models/component/ComponentModel"
import api from "../api/lunarverse"
import { AxiosResponse } from "axios"

export const fetchComponents = async (userId: string) => {
  const { data } = await api.get<ComponentModel[]>(`/component/list?user_id=${userId}`)
  return data
}

export const saveComponentAction = async (component: ComponentModel, userId: string): Promise<void> => {
  return await api.post(`/component?user_id=${userId}`, component)
}

export const runComponentAction = async (component: ComponentModel, userId: string) => {
  const { data } = await api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/component/run?user_id=${userId}`, component)
  return data
}

export const deleteComponentAction = async (componentId: string, userId: string): Promise<void> => {
  "use server"
  await api.delete(`/component/${componentId}?user_id=${userId}`)
}
