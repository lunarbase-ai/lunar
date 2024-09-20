// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Session, getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import api from '@/app/api/lunarverse';
import ModelsList from '@/components/models/ModelsList';
import { AIModel } from '@/models/ai_model/AIModel';

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let aiModels: AIModel[] = []
let aiModelTypes: AIModel[] = []

const listAIModelTypes = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<AIModel[]>(`/ai_model/types`)
    return data
  } else {
    redirect('/login')
  }
}

const listAIModels = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<AIModel[]>(`/ai_model?user_id=${session.user.email}`)
    return data
  } else {
    redirect('/login')
  }
}

export default async function Workflows() {
  const session = await getServerSession()
  if (session == null) redirect('/login')

  const saveAIModel = async (aiModel: AIModel): Promise<AIModel> => {
    "use server"
    if (session.user?.email) {
      const { data } = await api.post(`/ai_model?user_id=${session.user.email}`, aiModel)
      aiModels = await listAIModels(session)
      revalidatePath('/')
      return data
    } else {
      redirect('/login')
    }
  }

  const deleteAIModel = async (aiModelKey: string): Promise<void> => {
    "use server"
    if (session?.user?.email) {
      await api.delete(`/ai_model/${aiModelKey}?user_id=${session.user?.email}`)
      aiModels = await listAIModels(session)
      revalidatePath('/')
    } else {
      redirect('/login')
    }
  }

  try {
    aiModels = await listAIModels(session)
    aiModelTypes = await listAIModelTypes(session)
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
    <ModelsList
      aiModels={aiModels}
      aiModelTypes={aiModelTypes}
      saveAIModelConfiguration={saveAIModel}
      deleteAIModelConfiguration={deleteAIModel}
    />
  </div>
}