// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { AIModel, AIModelConnectionField } from "@/models/ai_model/AIModel"
import { Button, Form, Input, message } from "antd"
import { useState } from "react"

interface Props {
  aiModel: AIModel
  saveAIModelConfiguration: (aiModel: AIModel) => Promise<AIModel>
}

const GenericModelConfigurationForm: React.FC<Props> = ({ aiModel, saveAIModelConfiguration }) => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [messageApi, contextHolder] = message.useMessage()

  const mapFormValuesToAIModelConfig = (formValues: Record<string, string>) => {
    const newModel = aiModel
    const connectionSettings: AIModelConnectionField[] = []
    Object.keys(formValues).forEach(key => {
      const value = formValues[key]
      connectionSettings.push({ key, value })
    })
    newModel.connectionSettings = connectionSettings
    return newModel
  }

  return <>
    {contextHolder}
    <Form
      layout="vertical"
      onFinish={(values: Record<string, string>) => {
        setIsLoading(true)
        const filledModelConfig = mapFormValuesToAIModelConfig(values)
        saveAIModelConfiguration(filledModelConfig)
          .then(() => {
            messageApi.success('Your model configuration has been created successfully!')
          })
          .catch(() => {
            messageApi.error('Failed to create a new model configuration.')
          })
          .finally(() => {
            setIsLoading(false)
          })
      }}
    >
      {aiModel.connectionSettings.map(connectionSettingsField => <Form.Item
        key={connectionSettingsField.key}
        label={connectionSettingsField.key}
        name={connectionSettingsField.key}
        initialValue={connectionSettingsField.value}
        required
        rules={[{ required: true, message: 'This field is required' }]}
      >
        <Input />
      </Form.Item>)}
      <Form.Item style={{ textAlign: 'right' }}>
        <Button type="primary" htmlType="submit" loading={isLoading}>
          Save
        </Button>
      </Form.Item>
    </Form >
  </>
}

export default GenericModelConfigurationForm
