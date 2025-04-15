// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { DataSource } from '@/models/dataSource/DataSource';
import { getDataSourcesAction } from '@/app/actions/dataSources';
import DataSourceList from '@/components/dataSources/dataSourceList';

let dataSources: DataSource[] = []

export default async function DataSources() {
  const session = await getServerSession()
  const userId = session?.user?.email
  if (userId == null) redirect('/login')
  dataSources = await getDataSourcesAction(userId)

  return <DataSourceList
    dataSources={dataSources}
  />
}
