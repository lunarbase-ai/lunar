// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export const extractIdFromUrl = (url: string): string | null => {
  const regex = /\/(?:editor|workflow)\/([0-9a-fA-F-]{36})$/
  const match = url.match(regex)
  return match ? match[1] : null
}
