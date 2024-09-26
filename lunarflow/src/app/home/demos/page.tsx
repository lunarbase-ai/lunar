// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Session, getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'
import api from '@/app/api/lunarverse'
import DemoList from '@/components/demos/demoList/ComponentList'
import { WorkflowReference } from '@/models/Workflow'

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let workflowDemos: WorkflowReference[] = []

const listWorkflowDemos = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<WorkflowReference[]>(`/demo/list`)
    return data
  } else {
    redirect('/login')
  }
}

export default async function Components() {
  const session = await getServerSession()
  if (session == null) redirect('/login')
  try {
    workflowDemos = await listWorkflowDemos(session)
  } catch (error) {
    console.error(error)
    if (error instanceof AuthenticationError) {
      redirect('/login')
    }
  }
  return <div style={{
    display: 'flex',
    flexDirection: 'column',
    maxWidth: 800,
    width: '100%',
    flexGrow: 1,
    marginRight: 'auto',
    marginLeft: 'auto',
    gap: 8
  }}
  >
    <DemoList
      workflows={workflowDemos}
      session={session}
    />
  </div>
}