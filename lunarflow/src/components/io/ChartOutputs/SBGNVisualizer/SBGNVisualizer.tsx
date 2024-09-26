// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React from "react"
import cytoscape from "cytoscape"
import CytoscapeComponent from "../CytoscapeComponent"
import RedirectToExecutorOutput from "../../RedirectToExecutorOutput/RedirectToExecutorOutput"
const sbgnStylesheet = require("cytoscape-sbgn-stylesheet")
const convert = require("sbgnml-to-cytoscape")

interface SBGNGraph {
  'SBGN XML string': string
  'Selected node ids': string[]
}

interface Props {
  data: SBGNGraph
  pathname: string
}

const SBGNVisualizer: React.FC<Props> = ({ data, pathname }) => {
  if (pathname.includes('editor/')) {
    return <RedirectToExecutorOutput />
  }
  return <CytoscapeComponent
    elements={convert(data["SBGN XML string"])}
    nodeLabelsToSelect={data["Selected node ids"]}
    style={sbgnStylesheet(cytoscape)}
    layout={{
      name: 'cose',
      animate: true,
      animationThreshold: 250,
      fit: true,
      padding: 30,
      randomize: true,
      componentSpacing: 100,
      nodeRepulsion: (node) => 2048,
      nodeOverlap: 4,
      idealEdgeLength: (edge) => 32,
      edgeElasticity: (edge) => 32,
      nestingFactor: 1.2,
      gravity: 1,
      numIter: 1000,
      initialTemp: 1000,
      coolingFactor: 0.99,
      minTemp: 1.0
    }}
  />
}

export default SBGNVisualizer
