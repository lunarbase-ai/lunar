// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"
import api from "../api/lunarverse"

export const setEnvironmentVariablesAction = async (envVars: Record<string, string>, userId: string) => {
  const { data } = await api.post<Record<string, string>>(`/environment?user_id=${userId}`, envVars)
  return data
}

export const getEnvironmentVariablesAction = async (userId: string) => {
  const { data } = await api.get<Record<string, string>>(`/environment?user_id=${userId}`)
  return data
}
