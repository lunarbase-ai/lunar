// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Session, getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import api from '@/app/api/lunarverse';
import ComponentSearch from '@/components/components/ComponentSearch/ComponentSearch';
import ComponentsList from '@/components/components/ComponentList/ComponentList';
import { ComponentModel } from '@/models/component/ComponentModel';
import { Workflow } from '@/models/Workflow';

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let components: ComponentModel[] = []

const listComponents = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<ComponentModel[]>(`/component/list?user_id=${session.user.email}`)
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

export default async function Components() {
  const session = await getServerSession()
  if (session == null) redirect('/login')
  try {
    components = await listComponents(session)
  } catch (error) {
    console.error(error)
    if (error instanceof AuthenticationError) {
      redirect('/login')
    }
  }

  const createWorkflowFromComponentExample = async (componentLabel: string): Promise<Workflow> => {
    "use server"
    if (session?.user?.email) {
      const { data } = await api.get<Workflow>(`/component/${componentLabel}/example?user_id=${session.user.email}`)
      redirect(`/editor/${data.id}`)
    } else {
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
    <ComponentSearch />
    <ComponentsList
      components={components}
      session={session}
      deleteComponent={deleteComponent}
      createWorkflowFromComponentExample={createWorkflowFromComponentExample}
    />
  </div>
}
