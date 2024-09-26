// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
'use client'

import api from "@/app/api/lunarverse"
import { Workflow } from "@/models/Workflow"
import { Button, Form, Input, Modal } from "antd"
import { Session } from "next-auth"
import { useState } from "react"

async function autoCreateWorkflow(name: string, description: string, session: Session) {
  if (session?.user?.email) {
    const { data } = await api.post<Workflow>(`/auto_workflow?user_id=${session.user.email}`,
      {
        workflow: {
          name: name,
          description: description,
          userId: session.user.email,
          auto_component_spacing: { dx: 450, dy: 350, x0: 0, y0: 0 }
        },
      })
    return data
  }
  throw new Error('Unauthenticated user!')
}

interface AutoCreateWorkflowButtonProps {
  session: Session
  redirectToWorkflow: (workflowId: string) => void
}

interface AutoWorkflowFormInterface {
  workflowName: string,
  workflowDescription: string,
}

const AutoCreateWorkflowButton: React.FC<AutoCreateWorkflowButtonProps> = ({ session, redirectToWorkflow }) => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isSaveModalOpen, setIsSaveModalOpen] = useState<boolean>(false)


  const createRequest = (workflowName: string, workflowDescription: string) => {
    setIsLoading(true)
    autoCreateWorkflow(workflowName, workflowDescription, session)
      .then(({ id }) => {
        redirectToWorkflow(id)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  return <>
    <Button
      loading={isLoading}
      onClick={() => setIsSaveModalOpen(true)}
    >
      Auto-create workflow
    </Button>
    <Modal
      title="Auto-create workflow"
      open={isSaveModalOpen}
      onCancel={() => setIsSaveModalOpen(false)}
      footer={<></>}
    >
      <Form
        layout="vertical"
        onFinish={(values: AutoWorkflowFormInterface) => {
          setIsSaveModalOpen(false)
          createRequest(values.workflowName, values.workflowDescription)
        }}
        initialValues={{ // TODO: remove these hardcoded values
          workflowName: 'My auto-generated workflow',
          workflowDescription: 'Create a workflow where the first component is to upload PDFs from a local path, and the second component reads the uploaded PDF and outputs a dictionary with the sections and their contents.',
        }}
      >
        <Form.Item
          label="Workflow name"
          name="workflowName"
          rules={[{ required: true, message: 'Please name your workflow!' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="Generating Instruction"
          name="workflowDescription"
          rules={[{ required: true, message: 'Please write an instruction for generating a workflow!' }]}
        >
          <Input.TextArea rows={5} />
        </Form.Item>
        <Form.Item style={{ textAlign: 'right' }}>
          <Button type="primary" htmlType="submit">
            Auto-create
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  </>
}

export default AutoCreateWorkflowButton
