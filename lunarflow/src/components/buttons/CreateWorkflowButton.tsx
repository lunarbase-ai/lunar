// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'

import { createWorkflowAction } from "@/app/actions/workflows"
import { useUserId } from "@/hooks/useUserId"
import { Button } from "antd"
import { SessionProvider } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useState } from "react"


interface CreateWorkflowButtonProps { }

const CreateWorkflowButton: React.FC<CreateWorkflowButtonProps> = (props) => {
  return <SessionProvider>
    <CreateWorkflowButtonContent {...props} />
  </SessionProvider>
}

const CreateWorkflowButtonContent: React.FC<CreateWorkflowButtonProps> = () => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const userId = useUserId()
  const router = useRouter()

  const handleClick = () => {
    setIsLoading(true)
    if (userId) {
      createWorkflowAction('Untitled', '', userId)
        .then(({ id }) => {
          router.push(`/editor/${id}`)
        })
        .catch((error) => {
          console.error(error)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }

  return <Button
    loading={isLoading}
    onClick={handleClick}
  >
    Create workflow
  </Button>
}

export default CreateWorkflowButton
