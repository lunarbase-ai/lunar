// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import ComponentSearch from '@/components/components/ComponentSearch/ComponentSearch';
import DataSourcesList from '@/components/dataSources/DataSourcesList';
import { DataSource } from '@/models/dataSource/DataSource';
import { FileType, createDataSourceFromFiles, deleteDataSource, listDataSources } from '@/app/server_requests/data_source';
import { UploadFile } from 'antd';
import DataSourcesContainer from '@/components/dataSources/DataSourcesContainer';

class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

let dataSources: DataSource[] = []

export default async function DataSources() {
  const session = await getServerSession()
  const userId = session?.user?.email
  if (userId == null) redirect('/login')
  try {
    dataSources = await listDataSources(userId)
  } catch (error) {
    console.error(error)
    if (error instanceof AuthenticationError) {
      redirect('/login')
    }
  }

  const listDataSourcesWrapper = async (): Promise<DataSource[]> => {
    "use server"
    try {
      dataSources = await listDataSources(userId);
    } catch (error) {
      console.error(error);
    }
    return dataSources;
  }

  const deleteDataSourceWrapper = async (dataSourceName: string): Promise<void> => {
    "use server"
    try {
      await deleteDataSource(userId, dataSourceName);
      dataSources = await listDataSources(userId);
    } catch (error) {
      console.error(error);
    }
    return;
  }

  return <DataSourcesContainer
    dataSources={dataSources}
    listDataSources={listDataSourcesWrapper}
    deleteDataSource={deleteDataSourceWrapper}
  />
}
