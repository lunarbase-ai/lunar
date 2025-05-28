// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentInput } from "./ComponentInput"
import { ComponentOutput } from "./ComponentOutput"
import { ComponentPosition } from "./ComponentPosition"
import { Node } from "reactflow"

export interface ComponentModel {
  id?: string
  workflowId?: string
  name: string
  label?: string
  className: string
  description: string
  group: string
  inputs: ComponentInput[]
  output: ComponentOutput
  configuration: Record<string, string>
  version?: string
  isCustom: boolean
  isTerminal: boolean
  position?: ComponentPosition
  timeout: number
  componentCode: string | null
  componentCodeRequirements: string[]
  componentExamplePath?: string
  invalidErrors: string[]
  deleteNode?: () => void
  setNodes?: React.Dispatch<React.SetStateAction<Node<ComponentModel, string | undefined>[]>>
}

export function isComponentModel(obj: any): obj is ComponentModel {
  return (
    typeof obj === 'object' &&
    typeof obj.name === 'string' &&
    typeof obj.className === 'string' &&
    typeof obj.description === 'string' &&
    typeof obj.group === 'string' || obj.group === null &&
    Array.isArray(obj.inputs) &&
    typeof obj.output === 'object' &&
    typeof obj.configuration === 'object' &&
    typeof obj.isCustom === 'boolean' &&
    typeof obj.isTerminal === 'boolean' &&
    typeof obj.position === 'object'
  );
}

export enum ComponentDataType {
  FILE = "FILE",
  DATASOURCE = "DATASOURCE",
  TEXT = "TEXT",
  CODE = "CODE",
  R_CODE = "R_CODE",
  EMBEDDINGS = "EMBEDDINGS",
  JSON = "JSON",
  IMAGE = "IMAGE",
  REPORT = "REPORT",
  TEMPLATE = "TEMPLATE",
  LIST = "LIST",
  AGGREGATED = "AGGREGATED",
  PROPERTY_SELECTOR = "PROPERTY_SELECTOR",
  PROPERTY_GETTER = "PROPERTY_GETTER",
  GRAPHQL = "GRAPHQL",
  SQL = "SQL",
  SPARQL = "SPARQL",
  WORKFLOW = "WORKFLOW",
  PASSWORD = "PASSWORD",
  STREAM = "STREAM",
  CSV = "CSV",
  LINE_CHART = "LINE_CHART",
  BAR_CHART = "BAR_CHART",
}