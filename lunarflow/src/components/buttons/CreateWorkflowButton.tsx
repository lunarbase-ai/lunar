// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'

import { createWorkflowAction } from "@/app/actions/workflows"
import { useUserId } from "@/hooks/useUserId"
import { Button } from "antd"
import { useRouter } from "next/navigation"
import { useState } from "react"


interface CreateWorkflowButtonProps { }

const CreateWorkflowButton: React.FC<CreateWorkflowButtonProps> = () => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const userId = useUserId()
  const router = useRouter()

  const handleClick = async () => {
    setIsLoading(true)
    if (userId) {
      try {
        const workflow = await createWorkflowAction('Untitled', '', userId)
        router.push(`/editor/${workflow.id}`)
      } catch (e) {
        //TODO: Show feedback
        console.error(e)
      }
    }
    setIsLoading(false)
  }

  return <Button
    loading={isLoading || !userId}
    onClick={handleClick}
  >
    Create workflow
  </Button>
}

export default CreateWorkflowButton
