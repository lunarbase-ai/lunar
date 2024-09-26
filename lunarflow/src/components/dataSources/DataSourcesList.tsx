// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, Input, List, Modal, Spin, Typography, Upload, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled, InboxOutlined } from "@ant-design/icons"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { DataSource } from "@/models/dataSource/DataSource"
import { UploadFile } from "antd/es/upload"
import { createDataSourceFromFiles } from "@/app/server_requests/data_source"
import { useUserId } from "@/hooks/useUserId"
import assert from "assert"

const { confirm } = Modal
const { Link } = Typography
const { Dragger } = Upload

interface ComponentListProps {
  dataSources: DataSource[]
  deleteDataSource: (dataSourceName: string) => Promise<void>
  listDataSources: () => Promise<DataSource[]>
}

const DataSourcesList: React.FC<ComponentListProps> = ({
  dataSources,
  deleteDataSource,
  listDataSources,
}) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [uploading, setUploading] = useState(false)
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [dataSourceName, setDataSourceName] = useState<string>('')
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const router = useRouter()

  const showConfirm = (dataSourceId: string) => {
    confirm({
      title: 'Do you really want to delete this data source?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeDataSource(dataSourceId)
      },
      onCancel() {
      },
    })
  }

  const removeDataSource = (dataSourceName: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [dataSourceName]: true }))
    deleteDataSource(dataSourceName)
      .then(() => {
        messageApi.success('The data source has been deleted successfully')
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `Failed to delete data source. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [dataSourceName]: false }))
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

  const handleUpload = async () => {
    setUploading(true)
    try {
      assert(userId != null, 'User ID is null')
      await createDataSourceFromFiles(userId, fileList, dataSourceName);
      message.success('Data source uploaded successfully');
    } catch (error) {
      console.log(error);
      message.error('Failed to upload data source');
    }
    try {
      await listDataSources()
    } catch (error) {
      console.error(error)
      message.error('Failed to list data sources');
    }
    setUploading(false)
    setUploadModalOpen(false)
    setFileList([])
  }

  const onRemove = (file: UploadFile) => {
    const index = fileList.indexOf(file);
    const newFileList = fileList.slice();
    newFileList.splice(index, 1);
    setFileList(newFileList);
  }

  const beforeUpload = (file: UploadFile) => {
    setFileList([...fileList, file]);
    return false;
  }

  return <>
    {contextHolder}
    <List
      grid={{ gutter: 16, column: 2 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>Data Sources</div>
        <Button onClick={() => setUploadModalOpen(true)}>
          Create new data source
        </Button>
      </div>}
      itemLayout="horizontal"
      dataSource={dataSources}
      renderItem={(dataSource) => {
        const dataSourceId = dataSource.id
        if (dataSourceId == null) return <></>
        return <>
          <List.Item key={dataSourceId}>
            <Card
              title={<Link onClick={() => router.push(`/data_source/${dataSourceId}`)}>{dataSource.name}</Link>}
              extra={renderDeleteButton(dataSource)}
            >
              {dataSource.mimeType}
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
    <Modal
      title="Upload Data Source"
      open={uploadModalOpen}
      onCancel={() => setUploadModalOpen(false)}
      footer={[
        <Button key="cancel" onClick={() => setUploadModalOpen(false)}>
          Cancel
        </Button>,
        <Button
          key="upload"
          type="primary"
          onClick={handleUpload}
          disabled={fileList.length === 0 || dataSourceName === ''}
          loading={uploading}
        >
          {uploading ? 'Uploading...' : 'Start Upload'}
        </Button>,
      ]}
    >
      <Input
        placeholder="Data Source Name"
        value={dataSourceName}
        onChange={(e) => setDataSourceName(e.target.value)}
        style={{ marginBottom: 16 }}
      />
      <Dragger
        name="file"
        multiple
        onRemove={onRemove}
        beforeUpload={beforeUpload}
        fileList={fileList}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload</p>
        <p className="ant-upload-hint">
          Support for a single or bulk upload. Strictly prohibited from uploading company data or other
          banned files.
        </p>
      </Dragger>
    </Modal>
  </>
}

export default DataSourcesList