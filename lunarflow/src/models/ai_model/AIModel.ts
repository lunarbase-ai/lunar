// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export interface AIModel {
  key: string
  label: string
  description: string
  connectionSettings: AIModelConnectionField[]
}

export interface AIModelConnectionField {
  key: string
  value: string | null
}
