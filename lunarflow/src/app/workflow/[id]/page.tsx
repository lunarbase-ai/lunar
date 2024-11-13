// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import WorkflowExecutor from '@/components/workflowExecutor/WorkflowExecutor';
import { getWorkflowAction } from '@/app/actions/workflows';
import { getUserId } from '@/utils/getUserId';

export default async function WorkflowEditorPage({ params }: { params: { id: string } }) {
  const userId = await getUserId()
  const workflow = await getWorkflowAction(params.id, userId)

  return <WorkflowExecutor
    workflow={workflow}
  />
}
