// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use server"

import { redirect } from "next/navigation"
import GenerateInput from "@/components/generateInput"
import ComponentsList from '@/components/components/ComponentList/ComponentList';
import { ComponentModel } from '@/models/component/ComponentModel';
import { WorkflowReference } from '@/models/Workflow';
import DemoList from "@/components/demos/demoList/ComponentList";
import WorkflowList from "@/components/workflowList/WorkflowList";
import WelcomeCard from "@/components/welcome";
import RedirectButton from "@/components/buttons/redirectButton";
import { AuthenticationError } from "@/models/errors/authentication";
import { getUserId } from "@/utils/getUserId";
import { listWorkflowDemos, listWorkflowsAction } from "../actions/workflows";
import { getComponentsAction } from "../actions/components";

let components: ComponentModel[] = []
let workflowDemos: WorkflowReference[] = []
let workflows: WorkflowReference[] = []

export default async function HomePage() {

  const userId = await getUserId()

  try {
    components = await getComponentsAction(userId)
    workflowDemos = await listWorkflowDemos(userId)
    workflows = await listWorkflowsAction(userId)
  } catch (error) {
    if (error instanceof AuthenticationError) {
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
    <GenerateInput />
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    {workflows.length === 0 ? <></> : <>
      <WorkflowList
        workflows={workflows.slice(0, 6)}
      />
      <RedirectButton to="/home/workflows">See all workflows</RedirectButton>
    </>}
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    <ComponentsList
      components={components.slice(0, 6)}
    />
    <RedirectButton to="/home/components">See all components</RedirectButton>
    <div style={{ marginTop: 16, marginBottom: 16 }}></div>
    <DemoList
      workflows={workflowDemos.slice(0, 6)}
    />
    <RedirectButton to="/home/demos">See more use cases</RedirectButton>
  </div>
}
