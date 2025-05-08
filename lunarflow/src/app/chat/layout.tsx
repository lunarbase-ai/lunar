// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ConfigProvider, Layout } from 'antd';
import { Header } from '@/lib/layout';
import Image from 'next/image';
import Logo from '@/assets/Logo.png';
import { Content } from 'antd/es/layout/layout';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import ChatHeaderActions from '@/components/chat/chatHeaderActions';

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession()

  if (session == null) redirect('/login')
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#4DB1DD"
        }
      }}
    >
      <Layout style={{ height: '100%', backgroundColor: '#fff' }}>
        <Header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'rgba(255,255,255,0.5)',
          backdropFilter: 'blur(10px)',
          width: '100%',
          position: 'fixed',
          zIndex: 1,
        }}>
          <Image src={Logo} width={128} height={64} alt='Lunar' style={{ verticalAlign: 'middle' }} />
          <ChatHeaderActions />
        </Header>
        <Layout style={{ backgroundColor: '#fff' }}>
          <Content id='scroller' style={{
            overflowY: 'scroll',
          }}>
            {children}
            <div id='anchor'></div>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}
