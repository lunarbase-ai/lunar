// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Connection,
  Edge,
  Node,
  ReactFlowInstance,
  addEdge,
  useEdgesState,
  useNodesState,
  updateEdge,
  MarkerType
} from "reactflow";
import GenericCardTypeProps from "../cards/GenericCard/GenericCardTypeProps";
import { Workflow } from "@/models/Workflow";
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext";
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType";
import { GenericCard } from "../cards/GenericCard/GenericCard";
import './workspace.css';
import { ComponentModel } from "@/models/component/ComponentModel";
import WorkflowControls from "../workflowControls/WorkflowControls";
import { deleteNodeByLabel, loadWorkflow } from "@/utils/workflows";

const cardTypes: Record<string, React.FC<GenericCardTypeProps>> = {
  default: GenericCard,
}

interface WorkspaceProps {
  workflow: Workflow | null
}

const Workspace: React.FC<WorkspaceProps> = ({ workflow }) => {
  const reactFlowWrapper = useRef<HTMLDivElement | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState<ComponentModel>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType

  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null)

  useEffect(() => {
    const nodesCopy = [...nodes]
    nodesCopy.forEach(node => {
      if (node.data.label != null && workflowEditor.results[node.data.label] != null) {
        node.data.output = workflowEditor.results[node.data.label].output
        node.data.inputs = workflowEditor.results[node.data.label].inputs
      }
    })
    setNodes(nodesCopy)
  }, [workflowEditor.results])

  const getLabel = (type: string, nds: Node<ComponentModel>[]) => {
    let newId = 0
    const currentIds = new Set(nds.map(node => parseInt(node.id.replace(/\D/g, ''))))
    for (let i = 0; ; i++) {
      if (!currentIds.has(i)) {
        newId = i
        break
      }
    }
    return `${type.toUpperCase()}-${newId}`
  }

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge({
      ...params,
      updatable: 'target',
      type: 'smoothstep',
      style: { strokeWidth: 3, stroke: '#ccc' },
      markerEnd: {
        type: MarkerType.Arrow,
        width: 16,
        height: 16,
      }
    }, eds)),
    []
  );

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onEdgeUpdate = (oldEdge: Edge, newConnection: Connection) => {
    setEdges((els) => updateEdge(oldEdge, newConnection, els));
  }

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      if (reactFlowWrapper.current != null && reactFlowInstance != null) {
        event.preventDefault();

        const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect()
        const type = event.dataTransfer.getData('application/nodeType')
        const component = event.dataTransfer.getData('application/component')

        // check if the dropped element is valid
        if (typeof type === 'undefined' || !type) {
          return
        }

        const position = reactFlowInstance.project({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top,
        });

        setNodes((nds) => {
          const label = getLabel(type, nds)
          if (component != null && component.length > 0) {
            const parsedComponent: ComponentModel = JSON.parse(component)
            const nodeData: ComponentModel = {
              ...parsedComponent,
              workflowId: workflow?.id,
              label,
              deleteNode: () => deleteNodeByLabel(reactFlowInstance, label),
              setNodes,
            }
            const newNode: Node<ComponentModel> = {
              id: label,
              type: 'default',
              position,
              data: nodeData,
            };
            return nds.concat(newNode)
          }
          return nds
        });
      }
    },
    [reactFlowInstance]
  )

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }} ref={reactFlowWrapper}>
      {workflow != null ? <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={(instance) => {
          setReactFlowInstance(instance)
          loadWorkflow(instance, workflow, setValues)
        }}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={cardTypes}
        proOptions={{
          hideAttribution: true
        }}
        onEdgeUpdate={onEdgeUpdate}
        onNodesDelete={(nodes) => {
          setEdges(edges => {
            return edges
          })
        }}
      >
        <WorkflowControls />
        <Background style={{ backgroundColor: "#f6f6f6" }} variant={BackgroundVariant.Dots} gap={24} size={1} />
      </ReactFlow> : <>
        <Background style={{ backgroundColor: "#f6f6f6" }} variant={BackgroundVariant.Dots} gap={24} size={1} />
      </>}
    </div>
  );
}

export default Workspace
