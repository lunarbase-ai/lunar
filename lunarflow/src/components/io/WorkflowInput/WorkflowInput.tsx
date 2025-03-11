// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getWorkflowAction, listWorkflowsAction } from "@/app/actions/workflows";
import { useUserId } from "@/hooks/useUserId";
import { ComponentInput } from "@/models/component/ComponentInput";
import { Workflow, WorkflowReference } from "@/models/Workflow";
import { getWorkflowInputs } from "@/utils/workflows";
import { AutoComplete, Spin } from "antd"
import { useEffect, useState } from "react";

interface Props {
  value: Workflow
  onInputChange: (value: { newInputs: ComponentInput[], workflow: Workflow }) => void
}

const WorkflowInput: React.FC<Props> = ({
  value,
  onInputChange,
}) => {

  const userId = useUserId()
  const [workflows, setWorkflows] = useState<WorkflowReference[]>()
  const [autocompleteValue, setAutocompleteValue] = useState<string>()
  const [inputs, setInputs] = useState<ComponentInput[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
      if (!workflows && userId) {
          getWorkflows()
        }
        if (value?.id && userId && !autocompleteValue) {
            getWorkflowById(value.id)
        }
    }, [value, userId])
  //TODO: Add feedback
  if (!userId) return <></>


  const getWorkflows = () => {
    setIsLoading(true)
    listWorkflowsAction(userId)
      .then(workflows => {
        setWorkflows(workflows)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  const getWorkflowById = (workflowId: string) => {
    setIsLoading(true)
    getWorkflowAction(workflowId, userId)
      .then((workflow) => {
        setAutocompleteValue(workflow.name)
        const newInputs = Object.values(getWorkflowInputs(workflow)).reduce((allInputs, currentInput) => [...allInputs, ...currentInput], [])
        setInputs(newInputs)
        onInputChange({ newInputs, workflow })
        setIsLoading(false)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  return <>
    <AutoComplete
      value={autocompleteValue}
      options={workflows?.map(workflow => ({ key: workflow.id, value: workflow.name, id: workflow.id }))}
      onChange={(value) => setAutocompleteValue(value)}
      onFocus={getWorkflows}
      onSelect={(value, option) => getWorkflowById(option.id)}
    />
    <Spin spinning={isLoading} />
  </>
}

export default WorkflowInput
