// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React, { useContext, useEffect, useRef, useState } from "react"
import { Alert, Button, Divider, Form } from "antd"
import OutputHandle from "../../io/Handles/OutputHandle"
import { LunarFormerCard } from "../baseCard/LunarFormerCard"
import GenericCardTypeProps from "./GenericCardTypeProps"
import { useForm } from "antd/es/form/Form"
import ConfigurationModal from "../baseCard/ConfigurationModal"
import { Edge, useEdges, useNodes } from "reactflow"
import "./genericCardStyles.css"
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { ComponentModel } from "@/models/component/ComponentModel"
import { useParams } from "next/navigation"
import { getParameters } from "@/utils/helpers"
import WorkflowGenericInput from "@/components/io/GenericInput/WorkflowGenericInput"
import GenericOutput from "@/components/io/GenericOutput/GenericOutput"
import { CloseOutlined } from "@ant-design/icons"

export const GenericCard: React.FC<GenericCardTypeProps> = ({ data, id, type }) => {

  const [isConfigurationModalOpen, setIsConfigurationModalOpen] = useState<boolean>(false)
  const { workflowEditor } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const [edgeTargets, setEdgeTargets] = useState<Record<string, boolean>>({})
  const [forceRender, setForceRender] = useState<boolean>(false)
  const prevEdges = useRef<Edge[]>([])
  const [form] = useForm()
  const params = useParams()
  const nodes = useNodes<ComponentModel>()
  const edges = useEdges()
  const componentType = nodes.find(node => node.id === id)?.type ?? type

  useEffect(() => {
    data.inputs.forEach(input => {
      form.setFieldValue(input.key, input.value)
      const variableKeys = Object.keys(input.templateVariables)
      variableKeys.forEach((key) => {
        form.setFieldValue(key, input.templateVariables[key])
      })
    })
  }, [nodes])

  useEffect(() => {
    data.inputs.forEach(input => {
      updateInputOnEdgeChange(input.key)
      Object.keys(input.templateVariables).forEach(templateVariableKey => updateInputOnEdgeChange(`${templateVariableKey}`))
    })
  }, [edges])

  const generateTemplateVariables = (parameters: string[], fieldsValue: any) => {
    const templateVariables: Record<string, string> = {}
    Object.keys(fieldsValue).forEach(formField => {
      const [input, templateVariable] = formField.split('.')
      if (parameters.includes(templateVariable)) templateVariables[formField] = fieldsValue[formField]
    })
    return templateVariables
  }

  const syncNodesWithForm = () => {
    if (data.setNodes) data.setNodes((nds) => {
      return [...nds].map((node) => {
        if (node.id === id) {
          const fieldsValue = form.getFieldsValue(true)
          Object.keys(fieldsValue).forEach(formField => {
            const formFieldSplit = formField.split('.')
            const input = node.data.inputs.find(input => formFieldSplit.includes(input.key))
            if (input != null && formFieldSplit.length == 1) input.value = fieldsValue[formField]
            if (formFieldSplit[0] === input?.key && formFieldSplit.length > 1) {
              const parameters = typeof input.value === 'string' ? getParameters(input.value) : []
              input.templateVariables = generateTemplateVariables(parameters, fieldsValue)
            }
          })
        }
        return node
      })
    })
  }

  const onNameChange = (newName: string) => {
    if (data.setNodes) data.setNodes(nds => [...nds].map(node => {
      if (node.id === id) {
        node.data.name = newName
      }
      return node
    }))
  }

  const onInputChange = (inputKey: string, inputValue: any) => {
    setForceRender(prev => !prev)
    form.setFieldValue(inputKey, inputValue)
    syncNodesWithForm()
  }

  const updateInputOnEdgeChange = (inputKey: string) => {
    const inputEdge = edges.find(edge => edge.targetHandle === inputKey && edge.target === data.label)
    // Adding edge
    if (inputEdge != null) {
      const sourceNode = nodes.find(node => node.data.label === inputEdge.source)
      setEdgeTargets((prev) => {
        const copy = { ...prev }
        if (inputEdge.targetHandle) copy[`${data.label}.${inputEdge.targetHandle}`] = true
        return copy
      })
      onInputChange(inputKey, sourceNode?.data.output.value)
      prevEdges.current = edges
    }
    // Removing edge
    else {
      const currEdgeIds = edges.map(currEdge => currEdge.id)
      const deletedEdge = prevEdges.current.filter(prevEdge => !currEdgeIds.includes(prevEdge.id)).at(0)
      if (deletedEdge != null && deletedEdge.targetHandle === inputKey) {
        setEdgeTargets((prev) => {
          const copy = { ...prev }
          if (deletedEdge.targetHandle) copy[`${data.label}.${deletedEdge.targetHandle}`] = false
          return copy
        })
        onInputChange(inputKey, "")
        prevEdges.current = edges
      }
    }
  }

  return <>
    <ConfigurationModal
      id={id}
      configuration={data.configuration}
      open={isConfigurationModalOpen}
      close={() => { setIsConfigurationModalOpen(false) }}
      setNodes={data.setNodes!}
      component={data}
      type={componentType}
    />
    <LunarFormerCard
      id={id}
      component={data}
      setIsConfigurationModalOpen={setIsConfigurationModalOpen}
      onNameChange={onNameChange}
    >
      <Form layout="vertical" form={form}>
        {workflowEditor.errors
          .filter(error => typeof error === 'string')
          .filter(error => error.includes(data.label!))
          .map((error, index) => <Alert
            key={index}
            message={error.substring(0, 300)}
            type="error"
            showIcon
            className="nodrag nowheel"
            closable
            style={{ marginBottom: 16 }}
          />)}
        {data.inputs.map(
          (input, index) => <WorkflowGenericInput
            key={index + "." + input.key}
            form={form}
            inputKey={input.key}
            inputType={input.dataType}
            componentModel={data}
            nodeId={id}
            edgeTargets={edgeTargets}
            onInputChange={onInputChange}
          />
        )}
        <Divider style={{ margin: '16px 0', minWidth: 300 }} />

        <div style={{ marginTop: 16, maxHeight: 380 }}>
          {data.output.value && data.output.value !== ':undef:' ? (
            <>
              <div style={{ display: 'flex' }}>
                <div style={{ maxHeight: 380, overflowY: 'scroll', flexGrow: 1 }}>
                  <GenericOutput
                    workflowId={params['id'] as string}
                    outputDataType={data.output.dataType}
                    content={data.output.value}
                  />
                </div>
                <Button
                  onClick={() => {
                    data.setNodes &&
                      data.setNodes(nodes => {
                        return nodes.map(node =>
                          node.id === id ? { ...node, data: { ...node.data, output: { ...node.data.output, value: null } } } : node
                        );
                      });
                  }}
                  size="small"
                  type="text"
                  style={{ margin: 4 }}
                  icon={<CloseOutlined />}
                />
              </div>
              <OutputHandle name="" />
            </>
          ) : (
            <OutputHandle name="Output" />
          )}
        </div>
      </Form>
    </LunarFormerCard>
  </>
}
