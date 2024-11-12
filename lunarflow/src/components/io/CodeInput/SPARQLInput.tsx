// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { codeCompletionAction } from "@/app/actions/codeCompletion";
import { Button, Modal, message } from "antd"
import { AxiosError } from "axios";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react"

const DynamicCodeEditor = dynamic(
  () => import('./CodeEditor'),
  { ssr: false }
)

const defaultCode: string = `# Replace the below with a text starting with ## for LLM query completion.

# E.g. ## Some example should go here ...

# Some SPARQL query here ...
`

interface SPARQLInputProps {
  value: string
  codeCompletionApiKey: string | null
  openaiApiBase: string | null
  onInputChange: (value: string) => void
}

const SPARQLInput: React.FC<SPARQLInputProps> = ({
  value,
  codeCompletionApiKey,
  openaiApiBase,
  onInputChange,
}) => {

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [completionLoading, setCompletionLoading] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  const [editingCodeString, setEditingCodeString] = useState(defaultCode)
  const [messageApi, contextHolder] = message.useMessage()


  useEffect(() => {
    if (value.length > 0) {
      if (value !== ':undef:') setEditingCodeString(value)
    }
  }, [value])

  const handleOk = () => {
    onInputChange(editingCodeString)
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

  return <>
    {contextHolder}
    <Button style={{ width: '100%' }} onClick={() => setIsModalOpen(true)}>Edit query</Button>
    <Modal
      title="SPARQL Query"
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

export default SPARQLInput
