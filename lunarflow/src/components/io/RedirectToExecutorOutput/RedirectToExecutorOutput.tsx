// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { useUserId } from "@/hooks/useUserId"
import { ComponentModel } from "@/models/component/ComponentModel"
import { Workflow } from "@/models/Workflow"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { extractIdFromUrl } from "@/utils/paths"
import { getWorkflowFromView } from "@/utils/workflows"
import { SelectOutlined } from "@ant-design/icons"
import { Button, message } from "antd"
import { AxiosError } from "axios"
import { usePathname } from "next/navigation"
import { useRouter } from "next/navigation"
import { useState, useContext } from "react"
import { useNodes, useEdges } from "reactflow"

interface RedirectToExecutorOutputProps {
  saveWorkflowAction?: (workflow: Workflow, userId: string) => Promise<void>
}

const RedirectToExecutorOutput: React.FC<RedirectToExecutorOutputProps> = ({ saveWorkflowAction }) => {
  const router = useRouter()
  const pathname = usePathname()
  const userId = useUserId()
  const [isSaveLoading, setIsSaveLoading] = useState<boolean>(false)
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const reactflowNodes = useNodes<ComponentModel>()
  const reactflowEdges = useEdges<null>()
  const [messageApi] = message.useMessage()



  const saveAndRedirectWorkflow = async () => {
    if (!userId) {
      messageApi.error({
        content: 'You must be signed in to save a workflow'
      })
      return
    }
    const workflowId = extractIdFromUrl(pathname)
    if (!workflowId) {
      return
    }
    const workflow = getWorkflowFromView(workflowId, workflowEditor.name, workflowEditor.description, reactflowNodes, reactflowEdges, userId)
    setIsSaveLoading(true)
    try {
      if (saveWorkflowAction) await saveWorkflowAction(workflow, userId)
      setValues(undefined, undefined, [])
      messageApi.open({
        type: 'success',
        content: 'Your workflow has been saved'
      })
    } catch (err) {
      const error = err as AxiosError<{
        detail: string;
      }, any>
      setValues(undefined, undefined, [error.response?.data.detail ?? error.message])
      messageApi.error({
        content: 'Fail to save workflow'
      })
      console.error(error)
    }
    setIsSaveLoading(false)
    router.push(pathname.replace('/editor/', '/workflow/'))
  }

  return <>
    <Button
      onClick={saveAndRedirectWorkflow}
      icon={<SelectOutlined />}
      loading={isSaveLoading}
      style={{ width: '100%' }}
    >
      Open in Executor
    </Button>
  </>
}

export default RedirectToExecutorOutput
