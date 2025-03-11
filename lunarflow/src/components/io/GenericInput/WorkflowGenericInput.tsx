// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Form, FormInstance } from "antd"
import { useUpdateNodeInternals } from "reactflow"
import InputHandle from "../Handles/InputHandle"
import { useState } from "react"
import GenericInput from "./GenericInput"
import { ComponentDataType, ComponentModel } from "@/models/component/ComponentModel"
import TextInput from "../TextInput/TextInput"
import { ComponentInput } from "@/models/component/ComponentInput"
import { Workflow } from "@/models/Workflow"

interface Props {
  inputKey: string
  inputType: ComponentDataType
  componentModel: ComponentModel
  form: FormInstance
  nodeId: string
  edgeTargets: Record<string, boolean>
  onInputChange: (key: string, value: string) => void
}

const WorkflowGenericInput: React.FC<Props> = ({
  form,
  inputKey,
  inputType,
  componentModel,
  nodeId,
  edgeTargets,
  onInputChange,
}) => {
  const updateNodeInternals = useUpdateNodeInternals()
  const [parameters, setParameters] = useState<string[]>([])
  const isEdgeTarget = edgeTargets[`${nodeId}.${inputKey}`]

  const updateWorkflowInputs = (newInputs: ComponentInput[], workflow: Workflow) => {
    if (componentModel.setNodes) componentModel.setNodes(nds => [...nds].map(node => {
      if (node.id === nodeId) {
        const workflowInput = node.data.inputs.find(inp => inp.key === 'workflow')
        if (workflowInput) workflowInput.value = workflow.id
        const inputsArray: ComponentInput[] = workflowInput ? [workflowInput] : []
        console.log('>>>INPARR', inputsArray)
        inputsArray.push(...newInputs)
        node.data.inputs = inputsArray
      }
      return node
    }))
  }

  const handleChange = (key: string, value: any) => {
    if (inputType === ComponentDataType.WORKFLOW) {
      const { newInputs, workflow } = value
      updateWorkflowInputs(newInputs, workflow)
    } else {
      onInputChange(key, value)
    }
    updateNodeInternals(nodeId)
  }

  const updateParameters = (newParameters: string[]) => {
    newParameters.forEach(parameter => {
      const formKey = parameter
      if (form.getFieldValue(formKey) == null) {
        handleChange(formKey, '')
      }
    })
    setParameters(newParameters)
  }

  const isFormItemCollapsed =
    inputType === ComponentDataType.JSON ||
    inputType === ComponentDataType.REPORT ||
    inputType === ComponentDataType.EMBEDDINGS ||
    inputType === ComponentDataType.AGGREGATED ||
    isEdgeTarget

  return <>
    <Form.Item
      label={inputKey}
      labelAlign="left"
      required
      wrapperCol={isFormItemCollapsed ? { span: 24, style: { position: 'absolute' } } : { span: 24 }}
      labelCol={isFormItemCollapsed ? { style: { padding: 0, lineHeight: 2 } } : {}}
      style={isFormItemCollapsed ? { minHeight: 0 } : {}}
    >
      <InputHandle id={inputKey} />
      {isEdgeTarget ? <></> : <GenericInput
        inputKey={inputKey}
        value={form.getFieldValue(inputKey)}
        inputType={inputType}
        nodeId={nodeId}
        onInputChange={(inputKey, inputValue) => {
          handleChange(inputKey, inputValue)
        }}
        setParameters={updateParameters}
      />}
    </Form.Item>
    {isEdgeTarget ? <></> : parameters.map((param, i) => (
      <Form.Item
        key={i}
        label={param}
        labelAlign="left"
        required
        wrapperCol={edgeTargets[`${nodeId}.${param}`] ? { span: 24, style: { position: 'absolute' } } : { span: 24 }}
        labelCol={edgeTargets[`${nodeId}.${param}`] ? { style: { padding: 0, lineHeight: 2 } } : {}}
        style={edgeTargets[`${nodeId}.${param}`] ? { minHeight: 0 } : {}}
      >
        <InputHandle
          key={i}
          id={param}
        />
        {edgeTargets[`${nodeId}.${param}`]
          ? <></>
          : <TextInput
            key={param}
            value={form.getFieldValue(param)}
            onChange={text => {
              handleChange(param, text)
            }}
          />}
      </Form.Item>
    ))}
  </>
}

export default WorkflowGenericInput
