// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import DemoList from '@/components/demos/demoList/ComponentList'
import { WorkflowReference } from '@/models/Workflow'
import { listWorkflowDemosAction } from '@/app/actions/workflows'
import { getUserId } from '@/utils/getUserId'

let workflowDemos: WorkflowReference[] = []

export default async function Components() {
  const userId = await getUserId()

  workflowDemos = await listWorkflowDemosAction(userId)

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
    />
  </div>
}