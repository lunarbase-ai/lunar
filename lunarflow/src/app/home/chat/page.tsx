// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { redirect } from 'next/navigation';
import Chat from '@/components/chat/chat';
import { AuthenticationError } from '@/models/errors/authentication';
import { WorkflowReference } from '@/models/Workflow';
import { getUserId } from '@/utils/getUserId';
import { listWorkflowsAction } from '@/app/actions/workflows';

let workflows: WorkflowReference[] = []

export default async function ChatPage() {
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
    <Chat workflows={workflows} />
  </div>
}
