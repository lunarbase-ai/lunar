// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Session, getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { WorkflowReference } from '@/models/Workflow';
import { revalidatePath } from 'next/cache';
import WorkflowList from '@/components/workflowList/WorkflowList';
import WorkflowSearch from '@/components/workflowSearch/WorkflowSearch';
import api from '@/app/api/lunarverse';

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let workflows: WorkflowReference[] = []

const listWorkflows = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<WorkflowReference[]>(`/workflow/short_list?user_id=${session.user.email}`)
    return data
  } else {
    redirect('/login')
  }
}

const deleteWorkflow = async (session: Session, workflowId: string): Promise<void> => {
  "use server"
  if (session?.user?.email) {
    await api.delete(`/workflow/${workflowId}?user_id=${session.user?.email}`)
    workflows = await listWorkflows(session)
    revalidatePath('/')
  } else {
    redirect('/login')
  }
}

const redirectToWorkflowEditor = async (workflowId: string) => {
  "use server"
  redirect(`/editor/${workflowId}`)
}

const redirectToWorkflowView = async (workflowId: string) => {
  "use server"
  redirect(`/workflow/${workflowId}`)
}

export default async function Workflows() {
  const session = await getServerSession()
  if (session == null) redirect('/login')
  try {
    workflows = await listWorkflows(session)
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
    <WorkflowSearch />
    <div style={{ marginTop: 16 }}></div>
    <WorkflowList
      workflows={workflows}
      session={session}
      deleteWorkflow={deleteWorkflow}
      redirectToWorkflowEditor={redirectToWorkflowEditor}
      redirectToWorkflowView={redirectToWorkflowView}
    />
  </div>
}