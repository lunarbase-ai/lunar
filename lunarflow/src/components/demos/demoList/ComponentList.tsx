// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, List } from "antd"
import { useRouter } from "next/navigation"
import { WorkflowReference } from "@/models/Workflow"
import './styles.css'
import { useUserId } from "@/hooks/useUserId"
import { createWorkflowFromTemplateAction } from "@/app/actions/workflows"

interface Props {
  workflows: WorkflowReference[]
}

const DemoList: React.FC<Props> = ({ workflows }) => {
  const router = useRouter()
  const userId = useUserId()

  async function createWorkflow(templateId: string) {
    if (userId) {
      const result = await createWorkflowFromTemplateAction(templateId, userId)
      router.push(`/editor/${result.id}`)
    }
  }

  return <>
    <List
      grid={{ gutter: 16, column: 3 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{
          fontSize: 24,
          fontWeight: 'bold',
          color: '#0D181C',
          marginBottom: 16,
        }}>
          Use cases
        </h2>
      </div>}
      itemLayout="horizontal"
      dataSource={workflows}
      renderItem={(workflow) => {
        const workflowId = workflow.id
        if (workflowId == null) return <></>
        return <>
          <List.Item key={workflowId}>
            <Card
              title={workflow.name}
              extra={
                <Button
                  type="link"
                  onClick={() => {
                    createWorkflow(workflowId)
                  }}
                >
                  Try it out
                </Button>
              }
              style={{
                height: 255,
                display: 'flex',
                flexDirection: 'column',
              }}
              styles={{
                body: {
                  overflow: 'hidden',
                }
              }}
            >
              <p style={{
                height: '100%',
                overflow: 'hidden',
              }}>
                {workflow.description}
              </p>
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
  </>
}

export default DemoList