// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse"
import { useUserId } from "@/hooks/useUserId"
import { Workflow } from "@/models/Workflow"
import { ComponentModel, isComponentModel } from "@/models/component/ComponentModel"
import { CaretRightFilled } from "@ant-design/icons"
import { Button } from "antd"
import { AxiosError, AxiosResponse } from "axios"
import { useState } from "react"

interface Props {
  workflow: Workflow
  setComponentResults: (workflowResults: Record<string, ComponentModel>) => void
  setErrors: (errors: string[]) => void
}

const ExecutorButton: React.FC<Props> = ({ workflow, setComponentResults, setErrors }) => {
  const [isWorkflowRunning, setIsWorkflowRunning] = useState<boolean>(false)
  const userId = useUserId()

  const execute = async () => {
    setIsWorkflowRunning(true)
    setErrors([])
    api.post<any, AxiosResponse<Record<string, ComponentModel | string>, any>>(`/workflow/run?user_id=${userId}`, { ...workflow, userId })
      .then(response => {
        const { data } = response
        const componentResults: Record<string, ComponentModel> = {}
        const errors: string[] = []
        Object.keys(data).forEach(resultKey => {
          if (isComponentModel(data[resultKey])) {
            componentResults[resultKey] = data[resultKey] as ComponentModel
          } else {
            const error = data[resultKey] as string
            errors.push(error)
          }
        })
        setErrors(errors)
        setComponentResults(componentResults)
      })
      .catch((error: AxiosError<{ detail: any }>) => {
        setErrors([error.message])
        console.error(error)
      })
      .finally(() => {
        setIsWorkflowRunning(false)
      })
  }

  return <Button
    onClick={execute}
    loading={isWorkflowRunning}
    icon={<CaretRightFilled style={{ fontSize: 16 }} />}
    style={{ flexGrow: 1 }}
  >
    Run
  </Button>
}

export default ExecutorButton
