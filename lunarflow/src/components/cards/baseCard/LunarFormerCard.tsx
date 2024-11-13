// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React, { ReactNode, useContext } from "react"
import { Button, Card, Input, Tooltip, Typography } from "antd"
import { CaretRightOutlined, DeleteOutlined, SettingOutlined, WarningOutlined } from "@ant-design/icons"
import { ComponentModel, isComponentModel } from "@/models/component/ComponentModel"
import { AxiosError } from "axios"
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext";
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType";
import { useEdges, useNodes } from "reactflow"
import { useUserId } from "@/hooks/useUserId"
import { WorkflowRunningContext } from "@/contexts/WorkflowRunningContext"
import { WorkflowRunningType } from "@/models/workflowEditor/WorkflowRunningContext"
import { runComponentAction } from "@/app/actions/components"
import { convertClientToComponentModel } from "@/utils/workflows"

const { Text } = Typography

interface LunarFormerCardTitleProps {
  title: string
  tooltip?: string
  id: string
  onNameChange?: (newName: string) => void
}

const LunarFormerCardTitle: React.FC<LunarFormerCardTitleProps> = ({ title, tooltip, id, onNameChange }) => {
  return <div style={{ display: 'flex', flexDirection: 'column' }}>
    {tooltip != null ? <Tooltip title={tooltip} placement="topLeft">
      <Input
        style={{
          marginLeft: -12,
          color: 'var(--ant-color-text-heading)',
          fontWeight: 'var(--ant-font-weight-strong)',
          fontSize: 'var(--ant-card-header-font-size)',
        }}
        bordered={false}
        defaultValue={title}
        onChange={onNameChange ? (event) => onNameChange(event.target.value) : undefined}
      />
    </Tooltip> : <Input
      style={{
        marginLeft: -12,
        color: 'var(--ant-color-text-heading)',
        fontWeight: 'var(--ant-font-weight-strong)',
        fontSize: 'var(--ant-card-header-font-size)',
      }}
      bordered={false}
      defaultValue={title}
      onChange={onNameChange ? (event) => onNameChange(event.target.value) : undefined}
    />}
    <Text type="secondary" style={{ fontSize: 11, fontWeight: 400, lineHeight: '100%' }}>
      {id.split('-').at(0)}
    </Text>
  </div>
}

interface LunarFormerCardProps {
  children: ReactNode[] | ReactNode
  id: string
  component: ComponentModel
  setIsConfigurationModalOpen?: React.Dispatch<React.SetStateAction<boolean>>
  onNameChange?: (newName: string) => void
}

export const LunarFormerCard: React.FC<LunarFormerCardProps> = ({
  children,
  component,
  id,
  setIsConfigurationModalOpen,
  onNameChange,
}) => {
  const { isWorkflowRunning, setIsWorkflowRunning } = useContext(WorkflowRunningContext) as WorkflowRunningType
  const { setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const nodes = useNodes<ComponentModel>()
  const edges = useEdges()
  const userId = useUserId()

  const runComponent = async () => {
    setIsWorkflowRunning(true)
    setValues(undefined, undefined, [])
    if (!userId) return
    try {
      const linkedEdges = edges.filter(edge => edge.target === component.label)
      component.inputs.forEach(input => {
        const edge = linkedEdges.find(edge => input.key === edge.targetHandle)
        if (edge != null) {
          input.value = nodes.find(node => node.data.label === edge.source)?.data.output.value
        } else {
          Object.keys(input.templateVariables).forEach(variable => {
            const varEdge = linkedEdges.find(edge => variable === edge.targetHandle)
            if (varEdge != null) {
              input.templateVariables[variable] = nodes.find(node => node.data.label === varEdge.source)?.data.output.value
            }
          })
        }
      })
      const result = await runComponentAction(convertClientToComponentModel(component), userId)
      const componentResults: Record<string, ComponentModel> = {}
      const errors: string[] = []
      Object.keys(result).forEach(resultKey => {
        if (isComponentModel(result[resultKey])) {
          componentResults[resultKey] = result[resultKey] as ComponentModel
        } else {
          const error = result[resultKey] as string
          errors.push(`${resultKey}:${error}`)
        }
      })
      setValues(undefined, undefined, errors, componentResults)
    } catch (e) {
      if (e instanceof AxiosError) {
        const message = `${component.label}:${e.response?.data.detail}`
        setValues(undefined, undefined, [message])
      } else {
        console.error(e)
      }
    }

    setIsWorkflowRunning(false)
  }

  return <Card
    title={<LunarFormerCardTitle
      title={component.name ?? 'Custom'}
      tooltip={component.description ?? ''}
      id={id}
      onNameChange={onNameChange}
    />}
    extra={<div
      style={{ marginRight: -10 }}
    >
      {component.invalidErrors.length > 0 ?
        <Tooltip placement="top" title={component.invalidErrors.join('\n\n')}>
          <Button type="text" icon={<WarningOutlined style={{ color: '#f81d22' }} />} />
        </Tooltip>
        : <Button
          onClick={runComponent}
          type="text"
          icon={<CaretRightOutlined />}
          loading={isWorkflowRunning}
        />}
      {setIsConfigurationModalOpen != null ? <Button
        onClick={() => setIsConfigurationModalOpen(true)}
        type="text"
        icon={<SettingOutlined />}
      /> : <></>}
      <Button
        onClick={component.deleteNode}
        type="text"
        icon={<DeleteOutlined />}
      />
    </div>}
    style={{
      minWidth: 344,
      maxWidth: 344,
    }}
  >
    {Array.isArray(children) ? children.map(child => child) : children}
  </Card>
}
