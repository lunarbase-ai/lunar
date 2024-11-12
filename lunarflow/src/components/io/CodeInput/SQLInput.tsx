// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getParameters } from "@/utils/helpers";
import { Button, Modal, message } from "antd"
import { AxiosError } from "axios";
import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react"
import { Edge, useEdges, useNodes } from "reactflow";
import { ComponentModel } from "@/models/component/ComponentModel";
import { codeCompletionAction } from "@/app/actions/codeCompletion";

const DynamicCodeEditor = dynamic(
  () => import('./CodeEditor'),
  { ssr: false }
)

const defaultCode: string = `# Replace the below with a text starting with ## for LLM query completion.

# E.g. ## Some example should go here ...

# Some SQL query here ...
`

interface SQLInputProps {
  value: string
  codeCompletionApiKey: string | null
  openaiApiBase: string | null
  onInputChange: (value: string) => void
}

const SQLInput: React.FC<SQLInputProps> = ({
  value,
  codeCompletionApiKey,
  openaiApiBase,
  onInputChange,
}) => {

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [completionLoading, setCompletionLoading] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  const prevEdges = useRef<Edge[]>([])
  const nodes = useNodes<ComponentModel>()
  const edges = useEdges()
  const [editingCodeString, setEditingCodeString] = useState(defaultCode)
  const [messageApi, contextHolder] = message.useMessage()
  const [parameters, setParameters] = useState<string[]>([])


  useEffect(() => {
    if (value.length > 0) {
      if (value !== ':undef:') setEditingCodeString(value)
      setParameters(Array.from(new Set(getParameters(value ?? '').map(param => `${name}.${param}`))))
    }
  }, [value])

  const handleOk = () => {
    onInputChange(editingCodeString)
    setParameters(Array.from(new Set(getParameters(editingCodeString ?? '').map(param => `${name}.${param}`))))
    setIsModalOpen(false)
    setLoading(false)
  };

  const handleCancel = () => {
    setIsModalOpen(false)
    setLoading(false)
  }

  const queryCompletion = async () => {
    setCompletionLoading(true)
    try {
      const completion = await codeCompletionAction(editingCodeString)
      setEditingCodeString(completion)
    } catch (e) {
      const errorDetail = e as AxiosError<{ detail: string }>
      messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
    }
    setCompletionLoading(false)
  }

  useEffect(() => {
    parameters.forEach(parameter => updateInputOnEdgeChange(parameter))
  }, [edges])

  const updateInputOnEdgeChange = (inputKey: string) => {
    const inputEdge = edges.find(edge => edge.targetHandle === inputKey)
    if (inputEdge != null) {
      const connectedNode = nodes.find(node => node.data.label === inputEdge.source)
      onInputChange(connectedNode?.data.output.value)
    } else {
      const currEdgeIds = edges.map(currEdge => currEdge.id)
      const deletedEdge = prevEdges.current.filter(prevEdge => !currEdgeIds.includes(prevEdge.id)).at(0)
      if (deletedEdge != null && deletedEdge.targetHandle === inputKey) {
        onInputChange("")
      }
    }
    prevEdges.current = edges
  }

  return <>
    {contextHolder}
    <Button style={{ width: '100%' }} onClick={() => setIsModalOpen(true)}>Edit query</Button>
    <Modal
      title="SQL Query"
      open={isModalOpen}
      onOk={handleOk}
      onCancel={handleCancel}
      footer={[
        <Button
          key="completion"
          loading={completionLoading}
          onClick={queryCompletion}
        >
          Query completion
        </Button>,
        <Button key="back" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleOk}>
          Ok
        </Button>
      ]}
    >
      <DynamicCodeEditor
        value={editingCodeString}
        mode="mysql"
        onChange={(code) => setEditingCodeString(code)}
      />
    </Modal>
  </>
}

export default SQLInput
