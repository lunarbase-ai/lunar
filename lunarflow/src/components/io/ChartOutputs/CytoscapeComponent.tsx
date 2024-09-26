// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React, { useEffect, useRef } from 'react';
import cytoscape, { Core, Stylesheet, ElementsDefinition, LayoutOptions } from 'cytoscape'
import { message } from 'antd'

interface Props {
  elements: ElementsDefinition
  nodeLabelsToSelect?: string[]
  style?: Stylesheet[]
  layout: LayoutOptions
}

const CytoscapeComponent: React.FC<Props> = ({ elements, nodeLabelsToSelect, style, layout }) => {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef(null);
  const [messageApi, contextHolder] = message.useMessage()

  useEffect(() => {
    if (containerRef.current && !cyRef.current) {
      try {
        const cy = cytoscape({
          container: containerRef.current,
          elements: elements,
          style: style,
        })
        cy.layout(layout).run()
        cyRef.current = cy
      } catch (e) {
        console.error(e)
        messageApi.error("Failed to render the graph")
      }
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
        cyRef.current = null
      }
    };
  }, [])

  useEffect(() => {
    if (cyRef.current && nodeLabelsToSelect) {
      const cy = cyRef.current;
      cy.elements().unselect();
      nodeLabelsToSelect.forEach(label => {
        cy.elements(`node[label = "${label}"]`).select();
      });
    }
  }, [nodeLabelsToSelect])

  return <>
    {contextHolder}
    <div ref={containerRef} style={{ width: '100%', height: '500px' }} />
  </>;
};

export default CytoscapeComponent;