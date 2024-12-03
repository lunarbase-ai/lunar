// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import api from "@/app/api/lunarverse"
import { useUserId } from "@/hooks/useUserId"
import { Workflow, WorkflowReference } from "@/models/Workflow"
import { Card } from "antd"
import { SessionProvider } from "next-auth/react"
import { useRouter } from "next/navigation"

interface DemoCardProps {
  demo: WorkflowReference
}

const DemoCard: React.FC<DemoCardProps> = (props) => {
  return <SessionProvider>
    <DemoCardContent {...props} />
  </SessionProvider>
}

const DemoCardContent: React.FC<DemoCardProps> = ({ demo }) => {

  const userId = useUserId()
  const router = useRouter()

  async function createWorkflow(templateId: string) {
    if (userId) {
      const { data } = await api.post<Workflow>(`/workflow?user_id=${userId}&template_id=${templateId}`)
      router.push(`/editor/${data.id}`)
    } else {
      throw new Error('Unauthenticated user!')
    }
  }

  return <Card onClick={() => createWorkflow(demo.id)} style={{ cursor: 'pointer' }}>
    {demo.description}
  </Card>
}

export default DemoCard
