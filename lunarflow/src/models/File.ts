// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export interface File {
  path?: string
  name?: string
  type?: string
  data?: any
  size?: number
  preview?: string
}