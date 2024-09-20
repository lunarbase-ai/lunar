// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Workflow } from "@/models/Workflow"
import api from "../api/lunarverse"
import { AxiosError } from "axios"

export const saveWorkflow = async (
  userId: string | null,
  workflow: Workflow,
  onStart: () => void,
  onSuccess: () => void,
  onError: (error: AxiosError<{ detail: string }>) => void,
  onEnd: () => void,
) => {
  onStart()

  await api.put(`/workflow?user_id=${userId}`, workflow)
    .then(() => {
      onSuccess()
    })
    .catch((error: AxiosError<{ detail: string }>) => {
      onError(error)
    })
    .finally(() => {
      onEnd()
    })
}
