// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { redirect } from 'next/navigation';
import { WorkflowReference } from '@/models/Workflow';
import WorkflowSearch from '@/components/workflowSearch/WorkflowSearch';
import { AuthenticationError } from '@/models/errors/authentication';
import { listWorkflowsAction } from '@/app/actions/workflows';
import { getUserId } from '@/utils/getUserId';

let workflows: WorkflowReference[] = []

const deleteWorkflow = async (workflowId: string, userId: string): Promise<void> => {
  "use server"
  // await deleteWorkflowAction(workflowId, userId)
  // workflows = await listWorkflowsAction(userId)
  // revalidatePath('/')
}

const aaa = async () => {
  return
}

export default async function Workflows() {
  const userId = await getUserId()
  try {
    workflows = await listWorkflowsAction(userId)
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
    {/* <WorkflowList
      workflows={workflows}
      deleteWorkflow={aaa}
    /> */}
  </div>
}