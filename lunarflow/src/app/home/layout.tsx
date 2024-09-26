// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ConfigProvider, Layout } from 'antd';
import { Header } from '@/lib/layout';
import Image from 'next/image';
import Logo from '@/assets/Brand.png';
import AvatarDropdown from '@/components/AvatarDropdown';
import { Content } from 'antd/es/layout/layout';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import Sider from 'antd/es/layout/Sider';
import HomeMenu from '@/components/HomeMenu';

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession()

  if (session == null) redirect('/login')
  return (
    <ConfigProvider>
      <Layout style={{ height: '100%', backgroundColor: '#fff' }}>
        <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Image src={Logo} width={125} height={32} alt='Lunar' style={{ verticalAlign: 'middle' }} />
          <AvatarDropdown session={session} />
        </Header>
        <Layout style={{ backgroundColor: '#fff' }}>
          <Sider width={280} style={{ background: '#fff' }}>
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div style={{ flexGrow: 1, overflow: 'scroll' }}>
                <HomeMenu />
              </div>
            </div>
          </Sider>
          <Content style={{
            overflowY: 'scroll',
            marginRight: 16,
            marginLeft: 16
          }}>
            {children}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}
