// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse";
import { useUserId } from "@/hooks/useUserId";
import { ComponentInput } from "@/models/component/ComponentInput";
import { Workflow } from "@/models/Workflow";
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

  const [workflows, setWorkflows] = useState<Workflow[]>()
  const [autocompleteValue, setAutocompleteValue] = useState<string>()
  const [inputs, setInputs] = useState<ComponentInput[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const userId = useUserId()

  useEffect(() => {
    if (!workflows && userId) {
      getWorkflows()
    }
    if (value?.id && userId && !autocompleteValue) {
      getWorkflowById(value.id)
    }
  }, [value, userId])

  const getWorkflows = () => {
    setIsLoading(true)
    api.get<Workflow[]>(`workflow/short_list?user_id=${userId}`)
      .then(workflows => {
        setWorkflows(workflows.data)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  const getWorkflowById = (workflowId: string) => {
    setIsLoading(true)
    api.get<Workflow>(`workflow/${workflowId}?user_id=${userId}`)
      .then(({ data: workflow }) => {
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

  const handleChange = () => {

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
