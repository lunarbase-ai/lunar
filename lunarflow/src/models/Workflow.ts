// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentDependency } from "./component/ComponentDependency"
import { ComponentModel } from "./component/ComponentModel"

export interface WorkflowReference {
  id: string
  name: string
  description: string
  invalidErrors: string[]
}

export interface Workflow {
  id: string
  name: string
  description: string
  version?: string
  components: ComponentModel[]
  dependencies: ComponentDependency[]
  timeout?: number
  invalidErrors: string[]
}