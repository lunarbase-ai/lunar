// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "@/models/component/ComponentModel";

export default interface GenericCardTypeProps {
  data: ComponentModel
  type: string
  id: string
}