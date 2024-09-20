// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from '@/app/api/lunarverse';
import { Workflow } from '@/models/Workflow';
import { ComponentModel } from '@/models/component/ComponentModel';
import WorkflowEditor from '@/components/WorkfowEditor';
import { Session, getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';

const fetchComponents = async (session: Session) => {
  if (session.user?.email) {
    try {
      const { data } = await api.get<ComponentModel[]>(`/component/list?user_id=${session.user.email}`)
      return data
    } catch (error) {
      console.error(error)
      throw new Error('Fail to fetch components')
    }
  } else {
    throw new Error('Unauthenticated user!')
  }
}

const fetchWorkflow = async (id: string, session: Session) => {
  if (session.user?.email) {
    try {
      const { data } = await api.get<Workflow>(`/workflow/${id}?user_id=${session.user.email}`)
      return data
    } catch (error) {
      console.error(error)
      throw new Error('Fail to fetch workflow')
    }
  } else {
    throw new Error('Unauthenticated user!')
  }
}

export default async function WorkflowEditorPage({ params }: { params: { id: string } }) {
  const session = await getServerSession()

  if (!session) redirect('/login')

  const components = await fetchComponents(session)
  const workflow = await fetchWorkflow(params.id, session)

  return <WorkflowEditor
    workflowId={params.id}
    workflow={workflow}
    components={components}
    session={session}
  />
}
