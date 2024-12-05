// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentDataType } from "./ComponentModel"

export interface ComponentInput {
  id?: string
  key: string
  value: unknown
  dataType: ComponentDataType
  templateVariables: Record<string, string>
  componentId: string | null
}