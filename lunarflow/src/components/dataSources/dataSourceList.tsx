// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, Form, Input, List, Modal, Select, Spin, Typography, Upload, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled } from "@ant-design/icons"
import { useEffect, useState } from "react"
import { DataSource, DataSourceType } from "@/models/dataSource/DataSource"
import { useUserId } from "@/hooks/useUserId"
import { useForm } from "antd/es/form/Form"
import { createDataSourceAction, deleteDataSourceAction, listDataSourceTypesAction } from "@/app/actions/dataSources"
import DataSourceUploadModal from "./uploadModal"

const { confirm } = Modal
const { Item } = Form
const { Option } = Select
const { Dragger } = Upload

interface DataSourceProps {
  dataSources: DataSource[]
}

const DataSourceList: React.FC<DataSourceProps> = ({
  dataSources,
}) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false)
  const [creationLoading, setCreationLoading] = useState<boolean>(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [dataSourceTypes, setDataSourceTypes] = useState<DataSourceType[]>([])
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const [form] = useForm()

  useEffect(() => {
    if (userId) {
      listDataSourceTypesAction(userId).then(types => {
        setDataSourceTypes(types)
      })
    }
  }, [userId])
  if (!userId) return <></>

  const showConfirm = (dataSourceId: string) => {
    confirm({
      title: 'Do you really want to delete this data source connection?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeDataSource(dataSourceId)
      },
      onCancel() {
      },
    })
  }

  const removeDataSource = (dataSourceId: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [dataSourceId]: true }))
    deleteDataSourceAction(userId, dataSourceId)
      .then(() => {
        messageApi.success('The data source connection has been deleted successfully')
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `Failed to delete data source connection. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [dataSourceId]: false }))
      })
  }

  const renderDeleteButton = (dataSource: DataSource) => {
    const dataSourceName = dataSource.name
    if (dataSourceName == null) { return <></> }
    if (isLoading[dataSourceName]) { return <Spin /> }
    return <Button
      onClick={() => showConfirm(dataSourceName)}
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
    const dataSource: DataSource = {
      id: "",
      name: values['name'],
      description: values['description'],
      type: values['type'],
      connectionAttributes: connectionAttributes,
    }
    await createDataSourceAction(userId, dataSource)
    setCreationLoading(false)
  }

  const expectedConnectionAttributes = dataSourceTypes.find(type => {
    const fieldsValue = form.getFieldsValue()
    return 'type' in fieldsValue ? type.id === fieldsValue['type'] : false
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
        <div>Data Sources</div>
        <Button onClick={() => setModalOpen(true)}>
          Create new data source
        </Button>
      </div>}
      itemLayout="horizontal"
      dataSource={dataSources}
      renderItem={(dataSource) => {
        const dataSourceId = dataSource.id
        if (dataSourceId == null) return <></>
        return <>
          <List.Item key={dataSourceId} style={{ marginTop: 16 }}>
            <Card
              title={dataSource.name}
              extra={renderDeleteButton(dataSource)}
            >
              <div
                style={{ display: 'flex', flexDirection: 'column' }}
              >
                <Typography style={{ marginBottom: 16 }}>{dataSource.description}</Typography>
                {dataSource.type === 'LOCAL_FILE' ? <Button onClick={() => setIsUploadModalOpen(true)}>Upload file</Button> : <></>}
              </div>
            </Card>
          </List.Item>
          <DataSourceUploadModal
            dataSourceId={dataSourceId}
            dataSourceName={dataSource.name}
            open={isUploadModalOpen}
            onClose={() => setIsUploadModalOpen(false)}
          />
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
    <Modal
      title="Create data source connection"
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
          label="Data source connection name"
          rules={[{ required: true, message: 'Please add a name!' }]}
        >
          <Input />
        </Item>
        <Item
          layout="vertical"
          name="description"
          label="Data source connection description"
        >
          <Input />
        </Item>
        <Item
          layout="vertical"
          name="type"
          label="Data source type"
          rules={[{ required: true, message: 'Please add a type!' }]}
        >
          <Select>
            {dataSourceTypes.map(dataSourceType => <Option key={dataSourceType.id} value={dataSourceType.id}>
              {dataSourceType.name}
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

export default DataSourceList
