// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { listLLMsAction } from '@/app/actions/llms';
import LLMList from '@/components/llms/llmList';
import { LLM } from '@/models/llm/llm';

let llms: LLM[] = []

export default async function DataSources() {
  const session = await getServerSession()
  const userId = session?.user?.email
  if (userId == null) redirect('/login')
  llms = await listLLMsAction(userId)

  return <LLMList
    llms={llms}
  />
}
