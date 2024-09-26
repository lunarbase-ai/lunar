// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { WorkflowReference } from "@/models/Workflow"
import { Button, List, Modal, Space, Typography, message } from "antd"
import CreateWorkflowButton from "../buttons/CreateWorkflowButton"
import { Session } from "next-auth"
import { DeleteOutlined, ExclamationCircleFilled, SelectOutlined } from "@ant-design/icons"
import { useState } from "react"
import WorkflowListActions from "./WorkflowListActions"

const { confirm } = Modal
const { Link } = Typography

interface WorkflowListProps {
  workflows: WorkflowReference[]
  deleteWorkflow: (session: Session, workflowId: string) => Promise<void>
  redirectToWorkflowEditor: (workflowId: string) => void
  redirectToWorkflowView: (workflowId: string) => void
  session: Session
}

const WorkflowList: React.FC<WorkflowListProps> = ({ workflows, session, deleteWorkflow, redirectToWorkflowEditor, redirectToWorkflowView }) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [messageApi, contextHolder] = message.useMessage()

  const showConfirm = (workflowId: string) => {
    confirm({
      title: 'Do you really want to delete this workflow?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeWorkflow(workflowId)
      },
      onCancel() {
      },
    })
  }

  const removeWorkflow = (workflowId: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [workflowId]: true }))
    deleteWorkflow(session, workflowId)
      .then(() => {
        messageApi.success('The workflow has been deleted successfully')
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `There was a problem removing the workfow. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [workflowId]: false }))
      })
  }

  return <>
    {contextHolder}
    <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
      <h2 style={{
        fontSize: 24,
        fontWeight: 'bold',
        color: '#0D181C',
        marginBottom: 16,
      }}>
        Workflows
      </h2>
      <CreateWorkflowButton session={session} redirectToWorkflow={redirectToWorkflowEditor} />
      {/* <AutoCreateWorkflowButton session={session} redirectToWorkflow={redirectToWorkflowEditor} /> */}
    </Space>
    <List
      bordered
      itemLayout="horizontal"
      dataSource={workflows}
      renderItem={(item) => (
        <>
          <List.Item key={item.id}>
            <List.Item.Meta
              title={<Link onClick={() => redirectToWorkflowEditor(item.id)}>{item.name}</Link>}
              description={item.description}
            />

            <WorkflowListActions
              isLoading={isLoading[item.id]}
              items={[
                <Button
                  key={`delete_workflow_${item.id}`}
                  onClick={() => showConfirm(item.id)}
                  type="text"
                  icon={<DeleteOutlined />}
                  loading={isLoading[item.id]}
                />,
                <Button
                  key={`redirect_to_workflow_${item.id}`}
                  onClick={() => redirectToWorkflowView(item.id)}
                  type="text"
                  icon={<SelectOutlined />}
                  loading={isLoading[item.id]}
                />
              ]}
              errors={item.invalidErrors}
            />
          </List.Item>
        </>
      )}
      style={{
        marginTop: 16
      }}
    />
  </>
}

export default WorkflowList