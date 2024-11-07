// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Header } from "@/lib/layout"
import { Layout } from "antd"
import NewComponent from "./components/newComponent/NewComponent"

const NewComponentPage: React.FC = () => {

  const lunarverseOwner = process.env.LUNARVERSE_OWNER as string
  const lunarverseRepository = process.env.LUNARVERSE_REPOSITORY as string

  return <Layout style={{
    height: '100vh', backgroundColor: '#fff',
  }}>
    <Header />
    <Layout style={{ backgroundColor: '#fff', flexGrow: 1 }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        flexGrow: 1,
        marginRight: 'auto',
        marginLeft: 'auto',
        gap: 8
      }}
      >
        <NewComponent
          lunarverseOwner={lunarverseOwner}
          lunarverseRepository={lunarverseRepository}
        />
      </div>
    </Layout>
  </Layout>
}

export default NewComponentPage