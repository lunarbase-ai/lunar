// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse";
import { Button, Modal, message } from "antd"
import { AxiosError } from "axios";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react"

const DynamicCodeEditor = dynamic(
  () => import('./CodeEditor'),
  { ssr: false }
)

const defaultCode: string = `# Comments starting with ##
# will be interpreted as
# commands to LLM code completion

# E.g. ## Assign a list of 5 numbers to variable 'numbers'

# The output of the component
# will be the value you assign
# to 'result'
result = numbers
`

interface CodeInputProps {
  value: string
  codeCompletionApiKey: string | null
  openaiApiBase: string | null
  onInputChange: (value: string) => void
}

const CodeInput: React.FC<CodeInputProps> = ({
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

  const codeCompletion = async () => {
    setCompletionLoading(true)
    if (editingCodeString.includes('##')) {
      try {
        const { data: completion } = await api.post<string>('/code-completion', {
          code: editingCodeString,
          key: codeCompletionApiKey,
          base: openaiApiBase
        })
        setEditingCodeString(completion)
      } catch (e) {
        const errorDetail = e as AxiosError<{ detail: string }>
        messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
      }
    }
    setCompletionLoading(false)
  }

  return <>
    {contextHolder}
    <Button style={{ width: '100%' }} onClick={() => setIsModalOpen(true)}>Edit code</Button>
    <Modal
      title="Python coder"
      open={isModalOpen}
      onOk={handleOk}
      onCancel={handleCancel}
      footer={[
        <Button
          key="completion"
          loading={completionLoading}
          onClick={codeCompletion}
        >
          Code completion
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
        mode="python"
        onChange={(code) => setEditingCodeString(code)}
      />
    </Modal>
  </>
}

export default CodeInput
