// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, List, Typography } from "antd"
import { Session } from "next-auth"
import { useRouter } from "next/navigation"
import { Workflow, WorkflowReference } from "@/models/Workflow"
import api from "@/app/api/lunarverse"
import './styles.css'

const { Link } = Typography

interface Props {
  workflows: WorkflowReference[]
  session: Session
}

const DemoList: React.FC<Props> = ({ workflows, session }) => {
  const router = useRouter()

  async function createWorkflow(templateId: string, session: Session) {
    if (session?.user?.email) {
      const { data } = await api.post<Workflow>(`/workflow?user_id=${session.user.email}&template_id=${templateId}`)
      router.push(`/editor/${data.id}`)
    } else {
      throw new Error('Unauthenticated user!')
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
                  onClick={() => createWorkflow(workflowId, session)}
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