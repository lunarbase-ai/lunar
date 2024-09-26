// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { saveWorkflow } from "@/app/server_requests/workflow"
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { useUserId } from "@/hooks/useUserId"
import { ComponentModel } from "@/models/component/ComponentModel"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { extractIdFromUrl } from "@/utils/paths"
import { getWorkflowFromView } from "@/utils/workflows"
import { SelectOutlined } from "@ant-design/icons"
import { Button, message } from "antd"
import { usePathname } from "next/navigation"
import { useRouter } from "next/navigation"
import { useState, useContext } from "react"
import { useNodes, useEdges } from "reactflow"

const RedirectToExecutorOutput: React.FC = () => {
  const router = useRouter()
  const pathname = usePathname()
  const userId = useUserId()
  const [isSaveLoading, setIsSaveLoading] = useState<boolean>(false)
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const reactflowNodes = useNodes<ComponentModel>()
  const reactflowEdges = useEdges<null>()
  const [messageApi] = message.useMessage()

  const saveAndRedirectWorkflow = () => {
    const workflowId = extractIdFromUrl(pathname)
    if (!workflowId) {
      return
    }
    const workflow = getWorkflowFromView(workflowId, workflowEditor.name, workflowEditor.description, reactflowNodes, reactflowEdges, userId)
    saveWorkflow(
      userId,
      workflow,
      () => setIsSaveLoading(true),
      () => {
        setValues(undefined, undefined, [])
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
    ).then(() => {
      router.push(pathname.replace('/editor/', '/workflow/'))
    })
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
