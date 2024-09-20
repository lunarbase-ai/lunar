// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export interface ComponentDependency {
  id?: string
  componentInputKey: string | null
  templateVariableKey: string | null
  sourceLabel: string
  targetLabel: string
}