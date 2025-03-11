// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getWorkflowAction, listWorkflowsAction } from "@/app/actions/workflows";
import FetchSelect from "@/components/select/fetchSelect";
import { useUserId } from "@/hooks/useUserId";
import { ComponentInput } from "@/models/component/ComponentInput";
import { Workflow } from "@/models/Workflow";
import { getWorkflowInputs } from "@/utils/workflows";
import { Spin } from "antd"
import { useState } from "react";

interface Props {
  value: Workflow
  onInputChange: (value: { newInputs: ComponentInput[], workflow: Workflow }) => void
}

const WorkflowInput: React.FC<Props> = ({
  value,
  onInputChange,
}) => {

  const userId = useUserId()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  if (!userId) return <></>

  const getWorkflows = async () => {
    setIsLoading(true)
    const workflows = await listWorkflowsAction(userId)
    setIsLoading(false)
    return workflows?.map(workflow => ({ key: workflow.id, label: workflow.name, value: workflow.id }))
  }

  const getWorkflowById = (workflowId: string) => {
    setIsLoading(true)
    getWorkflowAction(workflowId, userId)
      .then((workflow) => {
        const newInputs = Object.values(getWorkflowInputs(workflow)).reduce((allInputs, currentInput) => [...allInputs, ...currentInput], [])
        onInputChange({ newInputs, workflow })
        setIsLoading(false)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }


  return <>
    <FetchSelect
      fetchOptions={getWorkflows}
      onChange={(event) => { if (!Array.isArray(event)) getWorkflowById(event.value) }}
    />
    <Spin spinning={isLoading} />
  </>
}

export default WorkflowInput
