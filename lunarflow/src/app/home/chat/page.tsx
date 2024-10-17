// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import api from '@/app/api/lunarverse';
import { Message } from '@/models/chat/message';
import { AxiosResponse } from 'axios';
import { ChatResponse } from '@/models/chat/chat';
import Chat from '@/components/chat/chat';
import { listWorkflows } from '@/lib/workflows';
import { AuthenticationError } from '@/models/errors/authentication';
import { WorkflowReference } from '@/models/Workflow';

let workflows: WorkflowReference[] = []

export default async function ChatPage() {
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

  const sendMessage = async (message: string, workflowIds: string[]) => {
    "use server"
    const user = session.user?.email ?? 'admin'
    const { data } = await api.post<any, AxiosResponse<ChatResponse, any>>(`/chat/generate?user_id=${user}`, {
      messages: [{ type: 'human', content: message }],
      workflows: workflowIds
    })
    console.log('>>>CHAT_RESULT', data)
    const responseMessage: Message = {
      content: data.summary,
      type: 'assistant'
    }
    return responseMessage
  }

  return <div style={{
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    maxWidth: 800,
    width: '100%',
    flexGrow: 1,
    marginRight: 'auto',
    marginLeft: 'auto',
    gap: 8,
    height: 'calc(100vh - 64px)'
  }}
  >
    <Chat onSubmit={sendMessage} session={session} workflows={workflows} />
  </div>
}
