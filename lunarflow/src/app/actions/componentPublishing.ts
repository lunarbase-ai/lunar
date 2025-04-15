// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { ComponentModel } from "@/models/component/ComponentModel"
import api from "../api/lunarverse"
import { AxiosError } from "axios"

export const generateComponentCodeAction = async (component: ComponentModel, userId: string): Promise<string> => {
  try {
    const req = await api.post<string>(`/component/generate_class_code?user_id=${userId}`, component)
    const componentCode = req.data
    return componentCode
  } catch (e) {
    const axiosError = e as AxiosError
    const data = axiosError.response?.data as any
    return ''
  }
}


export interface ComponentPublishingInput {
  author: string;
  author_email: string;
  component_name: string;
  component_description: string;
  component_class: string;
  component_documentation: string;
  version: string;
  access_token: string;
  user_id: string;
}

export const publishComponentAction = async (componentPublishingInput: ComponentPublishingInput, userId: string): Promise<void> => {
  try {
    await api.post<void>(`/component/publish?user_id=${userId}`, componentPublishingInput)
  } catch (e) {
    const axiosError = e as AxiosError
    console.error(axiosError)
  }
}