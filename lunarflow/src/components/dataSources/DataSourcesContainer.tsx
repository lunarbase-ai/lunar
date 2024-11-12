// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { SessionProvider } from "next-auth/react"
import DataSourcesList from "./DataSourcesList"
import { DataSource } from "@/models/dataSource/DataSource"

interface Props {
  dataSources: DataSource[]
  deleteDataSource: (dataSourceName: string) => Promise<void>
  listDataSources: () => Promise<DataSource[]>

}

const DataSourcesContainer: React.FC<Props> = ({
  dataSources,
  deleteDataSource,
  listDataSources,
}) => {
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
    <SessionProvider>
      <DataSourcesList
        dataSources={dataSources}
        deleteDataSource={deleteDataSource}
        listDataSources={listDataSources}
      />
    </SessionProvider>
  </div>
}

export default DataSourcesContainer
