// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Alert, Button, Card, List, Modal, Select, Spin, Typography, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled } from "@ant-design/icons"
import { useState } from "react"
import { AIModel } from "@/models/ai_model/AIModel"
import GenericModelConfigurationForm from "./GenericModelConfigurationForm"

const { confirm } = Modal
const { Link } = Typography

interface ComponentListProps {
  aiModels: AIModel[]
  aiModelTypes: AIModel[]
  saveAIModelConfiguration: (aiModel: AIModel) => Promise<AIModel>
  deleteAIModelConfiguration: (workflowId: string) => Promise<void>
}

const ModelsList: React.FC<ComponentListProps> = ({ aiModels, aiModelTypes, saveAIModelConfiguration, deleteAIModelConfiguration }) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false)
  const [selectedAiModelKey, setSelectedAiModelKey] = useState<string>('azure-gpt-4')
  const [messageApi, contextHolder] = message.useMessage()

  const renderDeleteButton = (aiModelKey: string) => {
    if (isLoading[aiModelKey]) { return <Spin /> }
    return <Button
      onClick={() => showConfirm(aiModelKey)}
      type="text"
      icon={<DeleteOutlined />}
      loading={isLoading[aiModelKey]}
    />
  }

  const showConfirm = (aiModelKey: string) => {
    confirm({
      title: 'Do you really want to delete this ai model configuration?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeAIModelConfiguration(aiModelKey)
      },
      onCancel() {
      },
    })
  }

  const removeAIModelConfiguration = (aiModelKey: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [aiModelKey]: true }))
    deleteAIModelConfiguration(aiModelKey)
      .then(() => {
        messageApi.success('The ai model configuration has been deleted successfully')
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `Failed to delete ai model configuration. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [aiModelKey]: false }))
      })
  }

  const selectedAiModelType = aiModelTypes.find(modelType => modelType.key === selectedAiModelKey)
  const aiModelTypeOptions = aiModelTypes.map(aiModelType => ({ value: aiModelType.key, label: aiModelType.label }))

  return <>
    {contextHolder}
    <List
      grid={{ gutter: 16, column: 2 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>Models</div>
        <Button onClick={() => setIsModalOpen(true)}>
          Create new model configuration
        </Button>
      </div>}
      itemLayout="horizontal"
      dataSource={aiModels}
      renderItem={(aiModel) => {
        const aiModelKey = aiModel.key
        if (aiModelKey == null) return <></>
        return <>
          <List.Item key={aiModelKey}>
            <Card
              title={<Link onClick={() => null}>{aiModel.label}</Link>}
              extra={renderDeleteButton(aiModel.key)}
            >
              {aiModel.description}
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
    <Modal
      title='Create new model configuration'
      open={isModalOpen}
      onCancel={() => setIsModalOpen(false)}
      footer={<></>}
    >
      <Select
        value={selectedAiModelKey}
        onChange={modelKey => setSelectedAiModelKey(modelKey)}
        style={{ width: '100%', marginBottom: 16 }}
        options={aiModelTypeOptions}
      />
      {selectedAiModelType != null ?
        <GenericModelConfigurationForm aiModel={selectedAiModelType} saveAIModelConfiguration={(aiModel) => {
          const newAIModel = saveAIModelConfiguration(aiModel)
          setIsModalOpen(false)
          return newAIModel
        }} /> :
        <Alert type="error" message='Sorry, this AI model is currently unavailable' />}
    </Modal>
  </>
}

export default ModelsList
