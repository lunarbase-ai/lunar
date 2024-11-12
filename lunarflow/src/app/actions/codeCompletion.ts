// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import api from "../api/lunarverse"

export const codeCompletionAction = async (code: string): Promise<string> => {
  if (code.includes('##')) {
    const { data: completion } = await api.post<string>('/code-completion', {
      code: code,
    })
    return completion
  } else {
    return code
  }
}
