// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "../component/ComponentModel"
import { WorkflowEditor } from "./WorkflowEditor"

export interface WorkflowEditorContextType {
  components: ComponentModel[]
  setComponents: (components: ComponentModel[]) => void
  workflowEditor: WorkflowEditor
  setValues: (name?: string, description?: string, errors?: string[], results?: Record<string, ComponentModel>) => void
}