// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
'use client'

import { autoCreateWorkflowAction } from "@/app/actions/copilot"
import { useUserId } from "@/hooks/useUserId"
import { Button, Form, Input, Modal } from "antd"
import { useState } from "react"

interface AutoCreateWorkflowButtonProps {
  redirectToWorkflow: (workflowId: string) => void
}

interface AutoWorkflowFormInterface {
  workflowName: string,
  workflowDescription: string,
}

const AutoCreateWorkflowButton: React.FC<AutoCreateWorkflowButtonProps> = ({ redirectToWorkflow }) => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isSaveModalOpen, setIsSaveModalOpen] = useState<boolean>(false)
  const userId = useUserId()

  const createRequest = (workflowName: string, workflowDescription: string) => {
    setIsLoading(true)
    if (userId) {
      autoCreateWorkflowAction(workflowName, workflowDescription, userId)
        .then(({ id }) => {
          redirectToWorkflow(id)
        })
        .catch((error) => {
          console.error(error)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }

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
