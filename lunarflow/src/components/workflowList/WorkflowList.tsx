// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { WorkflowReference } from "@/models/Workflow"
import { Button, List, Modal, Space, Typography, message } from "antd"
import CreateWorkflowButton from "../buttons/CreateWorkflowButton"
import { DeleteOutlined, ExclamationCircleFilled, SelectOutlined } from "@ant-design/icons"
import { useState } from "react"
import WorkflowListActions from "./WorkflowListActions"
import { useUserId } from "@/hooks/useUserId"
import { deleteWorkflowAction } from "@/app/actions/workflows"
import { SessionProvider } from "next-auth/react"
import { useRouter } from "next/navigation"

const { confirm } = Modal
const { Link } = Typography

interface WorkflowListProps {
  workflows: WorkflowReference[]
}

const WorkflowList: React.FC<WorkflowListProps> = (props) => {
  return <SessionProvider>
    <WorkflowListContent {...props} />
  </SessionProvider>
}

const WorkflowListContent: React.FC<WorkflowListProps> = ({ workflows }) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const router = useRouter()

  //TODO: show feedback
  if (!userId) return <></>

  const showConfirm = (workflowId: string) => {
    confirm({
      title: 'Do you really want to delete this workflow?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeWorkflow(workflowId)
        router.refresh()
      },
      onCancel() {
      },
    })
  }

  const removeWorkflow = (workflowId: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [workflowId]: true }))
    deleteWorkflowAction(workflowId, userId)
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
      <CreateWorkflowButton />
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
              title={<Link onClick={() => router.push(`/editor/${item.id}`)}>{item.name}</Link>}
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
                  onClick={() => router.push(`/workflow/${item.id}`)}
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