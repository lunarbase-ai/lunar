// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { redirect } from "next/navigation"
import { Button } from "antd"
import GenerateInput from "@/components/generateInput"
import { Session, getServerSession } from 'next-auth';
import { revalidatePath } from 'next/cache';
import api from '@/app/api/lunarverse';
import ComponentsList from '@/components/components/ComponentList/ComponentList';
import { ComponentModel } from '@/models/component/ComponentModel';
import { Workflow, WorkflowReference } from '@/models/Workflow';
import DemoList from "@/components/demos/demoList/ComponentList";
import WorkflowList from "@/components/workflowList/WorkflowList";
import WelcomeCard from "@/components/welcome";
import { MouseEventHandler } from "react";
import RedirectButton from "@/components/buttons/redirectButton";

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let components: ComponentModel[] = []
let workflowDemos: WorkflowReference[] = []
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

const redirectToDemos = async () => {
  "use server"
  redirect('/home/demos')
}

const redirectToComponents = async () => {
  "use server"
  redirect('/home/components')
}

const redirectToWorkflows = async () => {
  "use server"
  redirect('/home/workflows')
}

const listComponents = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<ComponentModel[]>(`/component/list?user_id=${session.user.email}`)
    return data
  } else {
    redirect('/login')
  }
}

const listWorkflowDemos = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<WorkflowReference[]>(`/demo/list`)
    return data
  } else {
    redirect('/login')
  }
}

const deleteComponent = async (session: Session, componentId: string): Promise<void> => {
  "use server"
  if (session?.user?.email) {
    await api.delete(`/component/${componentId}?user_id=${session.user.email}`)
    components = await listComponents(session)
    revalidatePath('/')
  } else {
    redirect('/login')
  }
}

export default async function HomePage() {

  const session = await getServerSession()
  if (session == null) redirect('/login')
  try {
    components = await listComponents(session)
    workflowDemos = await listWorkflowDemos(session)
    workflows = await listWorkflows(session)
  } catch (error) {
    console.error(error)
    if (error instanceof AuthenticationError) {
      redirect('/login')
    }
  }

  const createWorkflowFromComponentExample = async (componentId: string): Promise<Workflow> => {
    "use server"
    if (session?.user?.email) {
      const { data } = await api.get<Workflow>(`/component/${componentId}/example?user_id=${session.user.email}`)
      redirect(`/editor/${data.id}`)
    } else {
      redirect('/login')
    }
  }

  return <div style={{
    display: 'flex',
    flexDirection: 'column',
    maxWidth: 1200,
    width: '100%',
    flexGrow: 1,
    marginRight: 'auto',
    marginTop: 16,
    padding: 16,
    marginLeft: 'auto',
    gap: 8,
  }}
  >
    {workflows.length === 0 ? <WelcomeCard /> : <></>}
    <GenerateInput session={session} redirectToWorkflowEditor={redirectToWorkflowEditor} />
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    {workflows.length === 0 ? <></> : <>
      <WorkflowList
        workflows={workflows.slice(0, 6)}
        session={session}
        deleteWorkflow={deleteWorkflow}
        redirectToWorkflowEditor={redirectToWorkflowEditor}
        redirectToWorkflowView={redirectToWorkflowView}
      />
      <RedirectButton redirectToWorkflows={redirectToWorkflows}>See all workflows</RedirectButton>
    </>}
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    <ComponentsList
      components={components.slice(0, 6)}
      session={session}
      deleteComponent={deleteComponent}
      createWorkflowFromComponentExample={createWorkflowFromComponentExample}
    />
    <RedirectButton redirectToWorkflows={redirectToComponents}>See all components</RedirectButton>
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    <DemoList
      workflows={workflowDemos.slice(0, 6)}
      session={session}
    />
    <RedirectButton redirectToWorkflows={redirectToDemos}>See more use cases</RedirectButton>
  </div>
}
