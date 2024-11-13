// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { redirect } from 'next/navigation';
import ComponentSearch from '@/components/components/ComponentSearch/ComponentSearch';
import ComponentsList from '@/components/components/ComponentList/ComponentList';
import { ComponentModel } from '@/models/component/ComponentModel';
import { getComponentsAction } from '@/app/actions/components';
import { getUserId } from '@/utils/getUserId';

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let components: ComponentModel[] = []

export default async function Components() {
  const userId = await getUserId()
  try {
    components = await getComponentsAction(userId)
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
    <ComponentSearch />
    <ComponentsList
      components={components}
    />
  </div>
}
