// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React from "react"
import { ElementsDefinition } from "cytoscape"
import CytoscapeComponent from "../CytoscapeComponent"
import { Alert } from "antd"
import RedirectToExecutorOutput from "../../RedirectToExecutorOutput/RedirectToExecutorOutput"
import { Workflow } from "@/models/Workflow"

interface Props {
  data: object
  pathname: string
  saveWorkflowAction?: (workflow: Workflow, userId: string) => Promise<void>
}

function isElementsDefinition(data: any): data is ElementsDefinition {
  return (
    Array.isArray(data?.nodes) &&
    Array.isArray(data?.edges)
  );
}

const CytoscapeVisualizer: React.FC<Props> = ({
  data,
  pathname,
  saveWorkflowAction
}) => {

  try {
    const elements = data
    if (!isElementsDefinition(elements)) {
      throw new Error('Parsed data is not of type ElementsDefinition');
    }
    if (pathname.includes('editor/')) {
      return <RedirectToExecutorOutput saveWorkflowAction={saveWorkflowAction} />
    }
    return <CytoscapeComponent
      elements={elements}
      layout={{
        name: 'cose',
      }}
    />
  } catch (error) {
    return <Alert message={String(error)} type="error" />
  }
}

export default CytoscapeVisualizer
