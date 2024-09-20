// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "@/models/component/ComponentModel"
import { AutoComplete, Form } from "antd"
import { useEdges, useNodes, Node } from "reactflow"

function getLeafKeys(json: any, parentKey: string = ''): string[] {
  let leafKeys: string[] = [];

  for (const key in json) {
    if (json.hasOwnProperty(key)) {
      const currentKey = parentKey ? `${parentKey}.${key}` : key;

      if (typeof json[key] === 'object' && !Array.isArray(json[key])) {
        // Recursively call the function for nested objects
        leafKeys = leafKeys.concat(getLeafKeys(json[key], currentKey));
      } else {
        // Found a leaf node, add to the result
        leafKeys.push(currentKey);
      }
    }
  }

  return leafKeys;
}

interface PropertyGetterProps {
  value: string
  name: string
  nodeId: string
  onInputChange: (key: string, value: string) => void
}

const PropertyGetter: React.FC<PropertyGetterProps> = ({
  value,
  name,
  nodeId,
  onInputChange,
}) => {

  const edges = useEdges()
  const nodes = useNodes<ComponentModel>()

  const getProperties = () => {
    const inputNodeId = edges.filter(edge => edge.target === nodeId).at(0)?.source
    const inputNode: Node<ComponentModel> | undefined = nodes.find(node => node.id === inputNodeId)
    const options: { value: string }[] = getLeafKeys(inputNode?.data.output.value).map(key => ({ value: key }))
    return options
  }

  return <AutoComplete value={value} options={getProperties()} onChange={(value) => onInputChange(name, value)} />
}

export default PropertyGetter
