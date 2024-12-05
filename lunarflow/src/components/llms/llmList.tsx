// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, Form, Input, List, Modal, Select, Spin, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled } from "@ant-design/icons"
import { useEffect, useState } from "react"
import { useUserId } from "@/hooks/useUserId"
import { SessionProvider } from "next-auth/react"
import { DataSourceType, LLM } from "@/models/llm/llm"
import { createLLMAction, deleteLLMAction, listLLMTypesAction } from "@/app/actions/llms"
import { useForm } from "antd/es/form/Form"

const { confirm } = Modal
const { Item } = Form
const { Option } = Select

interface LLMListProps {
  llms: LLM[]
}

const LLMList: React.FC<LLMListProps> = (props) => {
  return <SessionProvider>
    <LLMListContent {...props} />
  </SessionProvider>
}

const LLMListContent: React.FC<LLMListProps> = ({
  llms,
}) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [creationLoading, setCreationLoading] = useState<boolean>(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [llmTypes, setLlmTypes] = useState<DataSourceType[]>([])
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const [form] = useForm()

  useEffect(() => {
    if (userId) {
      listLLMTypesAction(userId).then(types => {
        setLlmTypes(types)
      })
    }
  }, [userId])
  if (!userId) return <></>

  const showConfirm = (llmId: string) => {
    confirm({
      title: 'Do you really want to delete this LLM connection?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeLLM(llmId)
      },
      onCancel() {
      },
    })
  }

  const removeLLM = (llmId: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [llmId]: true }))
    deleteLLMAction(userId, llmId)
      .then(() => {
        messageApi.success('The LLM connection has been deleted successfully')
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `Failed to delete LLM connection. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [llmId]: false }))
      })
  }

  const renderDeleteButton = (llm: LLM) => {
    const llmName = llm.name
    if (llmName == null) { return <></> }
    if (isLoading[llmName]) { return <Spin /> }
    return <Button
      onClick={() => showConfirm(llmName)}
      type="text"
      icon={<DeleteOutlined />}
    />
  }

  const onFinish = async (values: Record<string, string>) => {
    setCreationLoading(true)
    const connectionAttributes: Record<string, string> = {}
    expectedConnectionAttributes.forEach(attribute => {
      if (attribute in values) {
        connectionAttributes[attribute] = values[attribute]
      }
    })
    const llm: LLM = {
      id: "",
      name: values['name'],
      description: values['description'],
      type: values['type'],
      connectionAttributes: connectionAttributes,
    }
    await createLLMAction(userId, llm)
    setCreationLoading(false)
  }

  const expectedConnectionAttributes = llmTypes.find(type => {
    const fieldsValue = form.getFieldsValue()
    return 'type' in fieldsValue ? type.name === fieldsValue['type'] : false
  })?.expectedConnectionAttributes ?? []

  return <div style={{
    display: 'flex',
    flexDirection: 'column',
    maxWidth: 800,
    width: '100%',
    flexGrow: 1,
    marginRight: 'auto',
    marginLeft: 'auto',
    gap: 8
  }}
  >
    {contextHolder}
    <List
      grid={{ gutter: 16, column: 2 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>LLMs</div>
        <Button onClick={() => setModalOpen(true)}>
          Create new LLM connection
        </Button>
      </div>}
      itemLayout="horizontal"
      dataSource={llms}
      renderItem={(llm) => {
        const llmId = llm.id
        if (llmId == null) return <></>
        return <>
          <List.Item key={llmId} style={{ marginTop: 16 }}>
            <Card
              title={llm.name}
              extra={renderDeleteButton(llm)}
            >
              {llm.description}
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
    <Modal
      title="Create LLM connection"
      footer={false}
      open={modalOpen}
      onCancel={() => setModalOpen(false)}
    >
      <Form
        form={form}
        layout="vertical"
        style={{
          display: 'flex',
          flexDirection: 'column',
          flexGrow: 1,
          height: '100%',
        }}
        onFinish={onFinish}
      >
        <Item
          layout="vertical"
          name="name"
          label="LLM connection name"
          rules={[{ required: true, message: 'Please add a name!' }]}
        >
          <Input />
        </Item>
        <Item
          layout="vertical"
          name="description"
          label="LLM connection description"
        >
          <Input />
        </Item>
        <Item
          layout="vertical"
          name="type"
          label="LLM type"
          rules={[{ required: true, message: 'Please add a type!' }]}
        >
          <Select>
            {llmTypes.map(llmType => <Option key={llmType.name} value={llmType.name}>
              {llmType.name}
            </Option>)}
          </Select>
        </Item>
        {expectedConnectionAttributes.map(attribute => <Item
          layout="vertical"
          name={attribute}
          label={attribute}
          rules={[{ required: true, message: `${attribute} is mandatory!` }]}
        >
          <Input />
        </Item>)}
        <Button type="primary" htmlType="submit" loading={creationLoading}>
          Ok
        </Button>
      </Form>

    </Modal>
  </div>
}

export default LLMList
