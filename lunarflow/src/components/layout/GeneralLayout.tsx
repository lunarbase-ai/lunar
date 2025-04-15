// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Layout } from "antd"
import { Header } from "antd/es/layout/layout"
import { ReactNode } from "react"

interface GeneralLayoutProps {
  children: ReactNode[] | ReactNode
}

const GeneralLayout: React.FC<GeneralLayoutProps> = ({ children }) => {
  return <Layout style={{ height: '100%', backgroundColor: '#fff' }}>
    <Header />
    <Layout style={{ backgroundColor: '#fff' }}>
      <div style={{
        maxWidth: 800,
        width: '100%',
        marginRight: 'auto',
        marginLeft: 'auto'
      }}
      >
        {Array.isArray(children) ? children.map(child => child) : children}
      </div>
    </Layout>
  </Layout>
}

export default GeneralLayout
