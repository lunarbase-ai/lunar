// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { BookOutlined, BulbOutlined, HomeOutlined, KeyOutlined, PartitionOutlined, UnorderedListOutlined } from "@ant-design/icons";
import { Menu, MenuProps } from "antd"
import { usePathname, useRouter } from "next/navigation"

type MenuItem = Required<MenuProps>['items'][number];

const items: MenuItem[] = [
  { key: '/home', label: 'Home', icon: <HomeOutlined /> },
  { key: '/home/demos', label: 'Demos', icon: <BulbOutlined /> },
  { key: '/home/workflows', label: 'Workflows', icon: <PartitionOutlined /> },
  { key: '/home/components', label: 'Components', icon: <UnorderedListOutlined /> },
  { key: '/home/environment', label: 'Environment', icon: <KeyOutlined /> },
  { key: 'documentation', label: 'Documentation', icon: <BookOutlined /> },
]

const HomeMenu = () => {
  const pathname = usePathname()
  const last = pathname.split("/").pop()
  const selectedItem = last != null ? [last] : []
  const router = useRouter()

  const onClick: MenuProps['onClick'] = (e) => {
    if (e.key == 'home') {
      router.push('/')
      return
    }
    if (e.key === 'documentation') {
      window.open("https://lunarbase-ai.github.io", "_blank")
    }
    router.push(`${e.key}`)
  };


  return <Menu
    mode="inline"
    onClick={onClick}
    selectedKeys={selectedItem}
    style={{ height: '100%', paddingTop: 32 }}
    items={items}
  />
}

export default HomeMenu
