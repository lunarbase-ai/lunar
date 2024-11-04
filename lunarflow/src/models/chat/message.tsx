// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "../component/ComponentModel"

export interface Message {
  content: string
  type?: string
  role?: string
  name?: string
  tool_calls?: any[]
  workflows_output?: Record<string, ComponentModel>
}
