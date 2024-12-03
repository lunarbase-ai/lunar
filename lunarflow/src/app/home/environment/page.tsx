// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import EnvironmentList from '@/components/environment/environmentList'
import { EnvironmentVariable } from '@/models/environmentVariable'
import { getEnvironmentVariablesAction } from '@/app/actions/environmentVariables';
import { getUserId } from '@/utils/getUserId';

let environmentVariables: EnvironmentVariable[] = []

export default async function Components() {
  const userId = await getUserId()
  try {
    const result = await getEnvironmentVariablesAction(userId)
    const environmentariablesArray = Object.keys(result).map(variableKey => {
      const environmentVariable: EnvironmentVariable = {
        key: variableKey,
        variable: variableKey,
        value: result[variableKey]
      }
      return environmentVariable
    })
    environmentVariables = environmentariablesArray
  } catch (error) {
    console.error(error)
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