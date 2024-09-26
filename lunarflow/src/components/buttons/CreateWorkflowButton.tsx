// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'

import api from "@/app/api/lunarverse"
import { Workflow } from "@/models/Workflow"
import { Button } from "antd"
import { Session } from "next-auth"
import { useState } from "react"

async function createWorkflow(name: string, description: string, session: Session) {
  if (session?.user?.email) {
    const { data } = await api.post<Workflow>(`/workflow?user_id=${session.user.email}`, { name, description, userId: session.user.email })
    return data
  }
  throw new Error('Unauthenticated user!')
}

interface CreateWorkflowButtonProps {
  session: Session
  redirectToWorkflow: (workflowId: string) => void
}

const CreateWorkflowButton: React.FC<CreateWorkflowButtonProps> = ({ session, redirectToWorkflow }) => {

  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleClick = () => {
    setIsLoading(true)
    createWorkflow('Untitled', '', session)
      .then(({ id }) => {
        redirectToWorkflow(id)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  return <Button
    loading={isLoading}
    onClick={handleClick}
  >
    Create workflow
  </Button>
}

export default CreateWorkflowButton
