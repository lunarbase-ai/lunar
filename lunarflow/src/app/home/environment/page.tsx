// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Session, getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'
import api from '@/app/api/lunarverse'
import EnvironmentList from '@/components/environment/environmentList'
import { EnvironmentVariable } from '@/models/environmentVariable'

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let environmentVariables: EnvironmentVariable[] = []

const listUserEnvironmentVariables = async (session: Session) => {
  if (session?.user?.email) {
    const { data } = await api.get<Record<string, string>>(`/environment?user_id=${session.user.email}`)
    return Object.keys(data).map(variableKey => {
      const environmentVariable: EnvironmentVariable = {
        key: variableKey,
        variable: variableKey,
        value: data[variableKey]
      }
      return environmentVariable
    })
  } else {
    redirect('/login')
  }
}

export default async function Components() {
  const session = await getServerSession()
  if (session == null) redirect('/login')
  try {
    environmentVariables = await listUserEnvironmentVariables(session)
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
    <EnvironmentList environmentVariables={environmentVariables} />
  </div>
}