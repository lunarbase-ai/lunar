// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { uploadFileToDataSourceAction } from "@/app/actions/dataSources"
import { useUserId } from "@/hooks/useUserId"
import { InboxOutlined } from "@ant-design/icons"
import { Button, GetProp, Modal, Upload, UploadFile, UploadProps } from "antd"
import { useRouter } from "next/navigation"
import { useState } from "react"
export type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const { Dragger } = Upload

interface DataSourceProps {
  dataSourceId: string;
  dataSourceName: string;
  open: boolean;
  onClose: () => void
}

const DataSourceUploadModal: React.FC<DataSourceProps> = ({
  dataSourceId,
  dataSourceName,
  open,
  onClose
}) => {

  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState<UploadFile | null>(null)
  const userId = useUserId()
  const router = useRouter()

  const onRemove = () => {
    setFile(null);
  }

  const beforeUpload = (file: UploadFile) => {
    setFile(file);
    return false;
  }

  const handleUpload = async () => {
    setUploading(true)
    //TODO: show feedback
    if (!userId || !file) return
    const formData = new FormData();
    formData.append('file', file as FileType);
    await uploadFileToDataSourceAction(userId, formData, dataSourceId)
    router.refresh()
    setUploading(false)
    onClose()
  }

  return <Modal
    title={`Upload file to ${dataSourceName} data source`}
    open={open}
    onCancel={onClose}
    footer={[
      <Button key="cancel" onClick={onClose}>
        Cancel
      </Button>,
      <Button
        key="upload"
        type="primary"
        onClick={handleUpload}
        disabled={!file}
        loading={uploading}
      >
        {uploading ? 'Uploading...' : 'Start Upload'}
      </Button>,
    ]}
  >
    <Dragger
      name="file"
      onRemove={onRemove}
      beforeUpload={beforeUpload}
    >
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">Click or drag file to this area to upload</p>
    </Dragger>
  </Modal>
}

export default DataSourceUploadModal
