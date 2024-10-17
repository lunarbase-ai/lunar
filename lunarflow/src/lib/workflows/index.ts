// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse"
import { WorkflowReference } from "@/models/Workflow"
import { Session } from "next-auth"
import { redirect } from "next/navigation"

export const listWorkflows = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<WorkflowReference[]>(`/workflow/short_list?user_id=${session.user.email}`)
    return data
  } else {
    redirect('/login')
  }
}