// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, Form, Input, List, Modal, Select, Spin, Typography, Upload, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled } from "@ant-design/icons"
import { useState } from "react"
import { DataSource, DataSourceCreationModel, DataSourceType } from "@/models/dataSource/DataSource"
import { useUserId } from "@/hooks/useUserId"
import { useForm } from "antd/es/form/Form"
import {
  createDataSourceAction,
  deleteDataSourceAction,
  getDataSourceTypesAction
} from "@/app/actions/dataSources"
import DataSourceUploadModal from "./uploadModal"
import { useRouter } from "next/navigation"

const { confirm } = Modal
const { Item } = Form
const { Option } = Select

interface File {
  fileName: string
  fileType: string
}

interface DataSourceProps {
  dataSources: DataSource[]
}

const DataSourceList: React.FC<DataSourceProps> = ({
  dataSources,
}) => {
  const [isSelectLoading, setIsSelectLoading] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [creationLoading, setCreationLoading] = useState<boolean>(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [filesModal, setFilesModal] = useState<boolean>(false)
  const [uploadModal, setUploadModal] = useState<boolean>(false)
  const [currentDatasource, setCurrentDatasource] = useState<DataSource | null>(null)
  const [dataSourceTypes, setDataSourceTypes] = useState<DataSourceType[]>([])
  const [expectedConnectionAttributes, setExpectedConnectionAttributes] = useState<string[]>([])
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const [form] = useForm()
  const router = useRouter()

  if (!userId) return <></>

  const files: File[] = currentDatasource?.connectionAttributes.files ?? []
  const fileNames = files.map(file => file.fileName.split('/').pop())

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
        router.refresh()
      })
  }

  const onSelectClick = () => {
    setIsSelectLoading(true)
    getDataSourceTypesAction(userId)
      .then(types => {
        setDataSourceTypes(types)
      })
      .finally(() => setIsSelectLoading(false))
  }

  const renderDeleteButton = (dataSource: DataSource) => {
    const dataSourceName = dataSource.name
    if (dataSourceName == null) { return <></> }
    if (isLoading[dataSourceName]) { return <Spin /> }
    return <Button
      onClick={() => showConfirm(dataSource.id)}
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
    const dataSource: DataSourceCreationModel = {
      name: values['name'],
      description: values['description'],
      type: values['type'],
      connectionAttributes: connectionAttributes,
    }
    await createDataSourceAction(userId, dataSource)
    setCreationLoading(false)
    setModalOpen(false)
    router.refresh()
  }

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
                {dataSource.type === 'LOCAL_FILE' && fileNames.length > 0 ? <Button
                  onClick={() => {
                    setCurrentDatasource(dataSource)
                    setFilesModal(true)
                  }}
                  style={{ marginBottom: 8 }}
                >
                  View files
                </Button> : <></>}
                {dataSource.type === 'LOCAL_FILE' ? <Button onClick={() => {
                  setCurrentDatasource(dataSource)
                  setUploadModal(true)
                }}>Upload file</Button> : <></>}
              </div>
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
    {currentDatasource && uploadModal && <DataSourceUploadModal
      dataSourceId={currentDatasource.id}
      dataSourceName={currentDatasource.name}
      open={!!currentDatasource}
      onClose={() => setCurrentDatasource(null)}
    />}
    {currentDatasource && filesModal && <Modal
      title="Files"
      footer={false}
      open={filesModal}
      onCancel={() => setFilesModal(false)}
    >
      <List
        dataSource={fileNames}
        renderItem={(fileName) => {
          return <List.Item>
            <Typography.Text>{fileName}</Typography.Text>
          </List.Item>
        }}
      />
    </Modal>}
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
          <Select
            value={form.getFieldValue('type')}
            onClick={onSelectClick}
            loading={isSelectLoading}
            onChange={(value) => {
              form.setFieldsValue({ type: value })
              const selectedDataSourceConnectionAttributes = dataSourceTypes.find(type => {
                const selectedType = form.getFieldValue('type')
                return selectedType === type.id
              })?.connectionAttributes ?? []
              setExpectedConnectionAttributes(selectedDataSourceConnectionAttributes)
            }}
          >
            {dataSourceTypes.map(dataSourceType => <Option key={dataSourceType.id} value={dataSourceType.id}>
              {dataSourceType.name}
            </Option>)}
          </Select>
        </Item>
        {expectedConnectionAttributes.map(attribute => <Item
          key={attribute}
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
