// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import WorkflowEditor from '@/components/WorkfowEditor';
import {
  getWorkflowAction
} from '@/app/actions/workflows';
import { getUserId } from '@/utils/getUserId';
import { getComponentsAction } from '@/app/actions/components';

export default async function WorkflowEditorPage({ params }: { params: { id: string } }) {
  const userId = await getUserId()

  const components = await getComponentsAction(userId)
  const workflow = await getWorkflowAction(params.id, userId)

  return <WorkflowEditor
    workflowId={params.id}
    workflow={workflow}
    components={components}
  />
}
