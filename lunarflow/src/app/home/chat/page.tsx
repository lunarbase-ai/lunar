// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
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
    minHeight: 'calc(100vh - 64px)'
  }}
  >
    <Chat session={session} workflows={workflows} />
  </div>
}
