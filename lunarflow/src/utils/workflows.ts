// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentDependency } from "@/models/component/ComponentDependency"
import { ComponentInput } from "@/models/component/ComponentInput"
import { ComponentDataType, ComponentModel } from "@/models/component/ComponentModel"
import { Workflow } from "@/models/Workflow"
import { Node, Edge, ReactFlowInstance, MarkerType } from "reactflow"

export const getWorkflowInputs = (workflow: Workflow) => {
  const inputs: Record<string, ComponentInput[]> = {}
  workflow.components.forEach(component => {
    inputs[component.label ?? 'EXTRA'] = []
    const componentInputTargets: string[] = []
    workflow.dependencies.filter(dependency => dependency.targetLabel === component.label).forEach(dep => {
      if (dep.componentInputKey != null) componentInputTargets.push(dep.componentInputKey)
      if (dep.templateVariableKey != null) componentInputTargets.push(dep.templateVariableKey)
    })
    component.inputs.forEach(input => {
      if ((
        !componentInputTargets.includes(input.key)
        // input.value === ':undef:' ||
        // input.value === undefined ||
        // input.value === '' ||
        // (input.dataType === ComponentDataType.FILE && input.value === 'upload')
      )) {
        inputs[component.label ?? 'EXTRA'].push(input)
      }
      Object.keys(input.templateVariables).forEach(templateVariable => {
        const value = input.templateVariables[templateVariable]
        if (
          // (value === ':undef:' || value === undefined || value === '') &&
          !componentInputTargets.includes(templateVariable)
        ) {
          const newInputFromTemplateVariable: ComponentInput = {
            key: `${component.label}:${templateVariable.replaceAll('.', '$')}`,
            value: value,
            dataType: ComponentDataType.TEXT,
            templateVariables: {},
            componentId: null
          }
          inputs[component.label ?? 'EXTRA'].push(newInputFromTemplateVariable)
        }
      })
    })
  })
  return inputs
}

// export const getWorkflowOutput = (workflow: Workflow) => {
//   if (workflow.dependencies.length > 0) {
//     const sources = workflow.dependencies.map(dependency => dependency.sourceLabel)
//     const targets = workflow.dependencies.map(dependency => dependency.targetLabel)
//     const output = targets.filter(target => !sources.includes(target))
//     if (output.length !== 1) {
//       return null
//     } else {
//       return workflow.components.filter(component => component.output.key === output.at(0)).at(0)?.output ?? null
//     }
//   } else {
//     if (workflow.components.length > 1) {
//       return null
//     } else {
//       return workflow.components.at(0)?.output ?? null
//     }
//   }
// }

export const getWorkflowOutput = (workflow: Workflow) => {
  const { dependencies, components } = workflow

  if (dependencies.length > 0) {
    const sources = dependencies.map(dep => dep.sourceLabel)
    const targets = dependencies.map(dep => dep.targetLabel)
    const output = targets.filter(target => !sources.includes(target))

    return output.length === 1
      ? components.find(component => component.output.key === output[0])?.output || null
      : null
  }

  return components.length === 1 ? components[0]?.output || null : null
}

export const getWorkflowOutputLabel = (workflow: Workflow) => {
  const { dependencies, components } = workflow

  if (dependencies.length > 0) {
    const sources = dependencies.map(dep => dep.sourceLabel)
    const targets = dependencies.map(dep => dep.targetLabel)
    const output = targets.filter(target => !sources.includes(target))

    return output.length === 1
      ? components.find(component => component.label === output.at(0))?.label || null
      : null
  }
  return components.length === 1 ? components.at(0)?.label || null : null
}

export const deleteNodeByLabel = (reactFlowInstance: ReactFlowInstance, label: string) => {
  reactFlowInstance.setNodes((nds) => nds.filter((node) => node.id !== label))
  reactFlowInstance.setEdges(edges => edges.filter(edge => edge.source !== label && edge.target !== label))
}

export const loadWorkflow = (
  reactFlowInstance: ReactFlowInstance,
  workflow: Workflow,
  setValues: (name?: string | undefined, description?: string | undefined, errors?: string[] | undefined, results?: Record<string, ComponentModel> | undefined) => void,
) => {
  setValues(workflow.name, workflow.description)
  reactFlowInstance.setNodes(workflow.components.map(component => ({
    id: component.label!,
    position: component.position || { x: 0, y: 0 },
    data: {
      ...component,
      setNodes: reactFlowInstance.setNodes,
      deleteNode: () => {
        deleteNodeByLabel(reactFlowInstance, component.label!)
      }
    }

  })))
  reactFlowInstance.setEdges(workflow.dependencies.map((dependency, index) => ({
    id: index.toString(),
    source: dependency.sourceLabel,
    target: dependency.targetLabel,
    targetHandle: dependency.templateVariableKey ?? dependency.componentInputKey,
    type: 'smoothstep',
    style: { strokeWidth: 3, stroke: '#ccc' },
    markerEnd: {
      type: MarkerType.Arrow,
      width: 16,
      height: 16,
    },
    data: dependency
  })))
}

export const getWorkflowFromView = (
  id: string,
  name: string,
  description: string,
  reactflowNodes: Node<ComponentModel>[],
  reactflowEdges: Edge<null>[],
  userId: string | null,
) => {
  const components: ComponentModel[] = reactflowNodes.map(node => ({
    ...node.data,
    group: node.data.group.replace(' ', '_'),
    label: node.id,
    position: node.position,
    workflowId: id
  }))
  const dependencies: ComponentDependency[] = reactflowEdges.map(edge => {
    const target = edge.targetHandle?.split('.')?.[0] ?? null
    const template = edge.targetHandle?.split('.')?.[1] ?? null
    return ({
      sourceLabel: edge.source,
      targetLabel: edge.target,
      componentInputKey: target,
      templateVariableKey: target && template ? `${target}.${template}` : null,
    })
  })
  const workflow: Workflow = {
    id,
    name,
    description,
    components,
    dependencies,
    invalidErrors: []
  }
  return workflow
}
