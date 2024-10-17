// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse"
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { CaretRightFilled, CloseSquareOutlined, CopyOutlined, RightOutlined, SaveOutlined } from "@ant-design/icons"
import { Button, Form, Input, List, Modal, Space, message } from "antd"
import { AxiosError, AxiosResponse } from "axios"
import React, { SVGProps, useContext, useState } from "react"
import { useEdges, useNodes, useReactFlow } from "reactflow"
import { Workflow } from "@/models/Workflow"
import { ComponentModel, isComponentModel } from "@/models/component/ComponentModel"
import { useUserId } from "@/hooks/useUserId"
import { WorkflowRunningContext } from "@/contexts/WorkflowRunningContext"
import { WorkflowRunningType } from "@/models/workflowEditor/WorkflowRunningContext"
import Icon from "@ant-design/icons/lib/components/Icon"
import { getWorkflowFromView, loadWorkflow } from "@/utils/workflows"
import { useSession } from "next-auth/react"
import { saveWorkflow } from "@/app/server_requests/workflow"

const MagicSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={16}
    height={16}
    fill="#3464DF"
    viewBox="0 0 24 24"
    {...props}
  >
    <path fill="none" d="M0 0h24v24H0z" />
    <path d="m19 9 1.25-2.75L23 5l-2.75-1.25L19 1l-1.25 2.75L15 5l2.75 1.25L19 9zm-7.5.5L9 4 6.5 9.5 1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5zM19 15l-1.25 2.75L15 19l2.75 1.25L19 23l1.25-2.75L23 19l-2.75-1.25L19 15z" />
  </svg>
)

interface Props {
  workflowId: string
  toggleCollapsed: () => void
  isCollapsed: boolean
}

interface WorkflowEditorFormInterface {
  workflowName: string,
  workflowDescription: string
}

interface WorkflowHistoryItem {
  workflow: Workflow
  prompt: string
}

const WorkflowActions: React.FC<Props> = ({ workflowId, isCollapsed, toggleCollapsed }) => {
  const { isWorkflowRunning, setIsWorkflowRunning } = useContext(WorkflowRunningContext) as WorkflowRunningType
  const [isCancelling, setIsCancelling] = useState<boolean>(false)
  const [isSaveLoading, setIsSaveLoading] = useState<boolean>(false)
  const [isSaveModalOpen, setIsSaveModalOpen] = useState<boolean>(false)
  const [isShareModalOpen, setIsShareModalOpen] = useState<boolean>(false)
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState<boolean>(false)
  const [generateInstruction, setGenerationInstruction] = useState<string>('')
  const [generationLoading, setGenerationLoading] = useState<boolean>(false)
  const userId = useUserId()
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const [generatedWorkflows, setGeneratedWorkflows] = useState<WorkflowHistoryItem[]>([])
  const { data: session } = useSession()
  const reactflowNodes = useNodes<ComponentModel>()
  const reactflowEdges = useEdges<null>()
  const instance = useReactFlow()
  const [messageApi, contextHolder] = message.useMessage()
  const origin: string = process.env.NEXT_PUBLIC_HOST ?? ''

  const execute = async () => {
    setIsWorkflowRunning(true)
    setValues(undefined, undefined, [])
    messageApi.destroy()
    const workflow = getWorkflowFromView(workflowId, workflowEditor.name, workflowEditor.description, reactflowNodes, reactflowEdges, userId)
    await api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/workflow/run?user_id=${session?.user?.email}`, workflow)
      .then(response => {
        const { data } = response
        const componentResults: Record<string, ComponentModel> = {}
        const errors: string[] = []
        Object.keys(data).forEach(resultKey => {
          if (isComponentModel(data[resultKey])) {
            componentResults[resultKey] = data[resultKey] as ComponentModel
          } else {
            const error = data[resultKey] as string
            errors.push(`${resultKey}:${error}`)
          }
        })
        setValues(undefined, undefined, errors, componentResults)
      })
      .catch((error: AxiosError<{ detail: string }>) => {
        messageApi.error({
          content: error.message ?? "There was a problem running the workfow",
          onClick: () => messageApi.destroy()
        }, 0)
        console.error(error)
      })
      .finally(() => {
        setIsWorkflowRunning(false)
      })
  }

  const cancel = async () => {
    setIsCancelling(true)
    setValues(undefined, undefined, [])
    messageApi.destroy()
    await api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/workflow/${workflowId}/cancel?user_id=${session?.user?.email}`)
      .then(response => {
        const { data } = response
        const componentResults: Record<string, ComponentModel> = {}
        const errors: string[] = []
        Object.keys(data).forEach(resultKey => {
          if (isComponentModel(data[resultKey])) {
            componentResults[resultKey] = data[resultKey] as ComponentModel
          } else {
            const error = data[resultKey] as string
            errors.push(`${resultKey}:${error}`)
          }
        })
        setValues(undefined, undefined, errors, componentResults)
      })
      .catch((error: AxiosError<{ detail: string }>) => {
        messageApi.error({
          content: error.message ?? "There was a problem cancelling the workfow",
          onClick: () => messageApi.destroy()
        }, 0)
        console.error(error)
      })
      .finally(() => {
        setIsCancelling(false)
      })
  }

  const generateWorkflow = async (instruction: string) => {
    setGenerationLoading(true)
    const currentWorkflow = getWorkflowFromView(workflowId, workflowEditor.name, workflowEditor.description, reactflowNodes, reactflowEdges, userId)
    const { data: newWorkflow } = await api.post<Workflow>(`/auto_workflow_modification?user_id=${userId}&modification_instruction=${instruction}`, {
      workflow: currentWorkflow
    })
    loadWorkflow(instance, newWorkflow, setValues)
    setGeneratedWorkflows([...generatedWorkflows, { workflow: newWorkflow, prompt: instruction }])
    setGenerationLoading(false)
  }

  return <>
    {contextHolder}
    <div style={{ position: 'absolute', top: 0, right: 0 }}>
      <Space.Compact
        style={{ paddingTop: 14, paddingLeft: 16, paddingRight: 16, width: '100%' }}
      >
        <Button
          onClick={execute}
          loading={isWorkflowRunning}
          icon={<CaretRightFilled style={{ fontSize: 16 }} />}
          style={{ flexGrow: 1 }}
        >
          Run
        </Button>
        <Button
          onClick={cancel}
          loading={isCancelling}
          disabled={!isWorkflowRunning}
          icon={<CloseSquareOutlined style={{ fontSize: 16 }} />}
          style={{ flexGrow: 1 }}
        >
          Cancel
        </Button>
        <Button
          onClick={() => setIsSaveModalOpen(true)}
          loading={isSaveLoading}
          icon={<SaveOutlined style={{ fontSize: 16 }} />}
          style={{ flexGrow: 1 }}
        >
          Save
        </Button>
        {/* <Button
          onClick={() => setIsShareModalOpen(true)}
          icon={<ShareAltOutlined style={{ fontSize: 16 }} />}
          style={{ flexGrow: 1 }}
        >
          Share
        </Button> */}
        <Button
          onClick={toggleCollapsed}
          icon={isCollapsed ? <Icon component={() => MagicSvg({ style: { fill: '#3464DF' } })} style={{ fontSize: 16 }} /> : <RightOutlined />}
          style={{ flexGrow: 1 }}
        >
          {isCollapsed ? 'Generate' : 'Close'}
        </Button>
      </Space.Compact>
    </div>
    <Modal
      title="Save workflow"
      open={isSaveModalOpen}
      okButtonProps={{ disabled: workflowEditor.name.length === 0 }}
      onCancel={() => setIsSaveModalOpen(false)}
      footer={<></>}
    >
      <Form
        layout="vertical"
        onFinish={(values: WorkflowEditorFormInterface) => {
          setValues(values.workflowName, values.workflowDescription)
          setIsSaveModalOpen(false)
          const workflow = getWorkflowFromView(workflowId, values.workflowName, values.workflowDescription, reactflowNodes, reactflowEdges, userId)
          saveWorkflow(
            userId,
            workflow,
            () => setIsSaveLoading(true),
            () => {
              setValues(undefined, undefined, [])
              setIsSaveModalOpen(false)
              messageApi.open({
                type: 'success',
                content: 'Your workflow has been saved'
              })
            },
            (error) => {
              setValues(undefined, undefined, [error.response?.data.detail ?? error.message])
              console.error(error)
            },
            () => {
              setIsSaveLoading(false)
            }
          )
        }}
        initialValues={{
          workflowName: workflowEditor.name,
          workflowDescription: workflowEditor.description
        }}
      >
        <Form.Item
          label="Workflow name"
          name="workflowName"
          rules={[{ required: true, message: 'Please name your workflow' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="Workflow description"
          name="workflowDescription"
          rules={[{ required: true, message: 'Please write a description' }]}
        >
          <Input.TextArea rows={5} />
        </Form.Item>
        <Form.Item style={{ textAlign: 'right' }}>
          <Button type="primary" htmlType="submit">
            Save
          </Button>
        </Form.Item>
      </Form>
    </Modal>
    <Modal
      title="Share workflow"
      open={isShareModalOpen}
      onOk={() => setIsShareModalOpen(false)}
      onCancel={() => setIsShareModalOpen(false)}
      footer={<Button type="primary" onClick={() => setIsShareModalOpen(false)}>Ok</Button>}
    >
      <Space.Compact style={{ width: '100%' }}>
        <Input value={`${origin}/workflow/${workflowId}`} readOnly />
        <Button
          onClick={() => navigator.clipboard.writeText(`${origin}/workflow/${workflowId}`).then(() => messageApi.open({
            type: 'success',
            content: 'Copied to clipboard',
          }))}
          icon={<CopyOutlined />}
        />
      </Space.Compact>
    </Modal>
    <Modal
      title="Generate"
      open={isGenerateModalOpen}
      onOk={() => setIsGenerateModalOpen(false)}
      onCancel={() => setIsGenerateModalOpen(false)}
      footer={<>
        <Button
          type="primary"
          loading={generationLoading}
          onClick={() => generateWorkflow(generateInstruction)}
          icon={<Icon component={() => MagicSvg({ style: { fill: '#fff' } })} style={{ fontSize: 16 }} />}
        >
          Generate
        </Button>
      </>}
    >
      {generatedWorkflows.length > 0 ? <List
        dataSource={generatedWorkflows}
        renderItem={(workflow) => <List.Item
          actions={[<Button key='load' onClick={() => loadWorkflow(instance, workflow.workflow, setValues)}>Load</Button>]}
        >
          {workflow.prompt}
        </List.Item>}
      /> : <></>}
      <Input.TextArea
        value={generateInstruction}
        onChange={event => setGenerationInstruction(event.target.value)}
        placeholder="Generate a Lunar Workflow from text..."
        autoSize
        autoFocus
      />
    </Modal>
  </>
}

export default WorkflowActions
