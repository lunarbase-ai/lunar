// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'

import { UserOutlined } from "@ant-design/icons"
import { Avatar, Dropdown, MenuProps } from "antd"
import { Session } from "next-auth"
import { SessionProvider, signOut, useSession } from "next-auth/react"

const items: MenuProps['items'] = [
  {
    key: '1',
    label: (
      <span onClick={() => signOut({ callbackUrl: '/' })}>
        Log out
      </span>
    ),
  }, {
    key: '2',
    label: (
      <span onClick={() => signOut({ callbackUrl: '/' })}>
        Settings
      </span>
    ),
  }
]

interface AvatarDropdownProps { }

const AvatarDropdown: React.FC<AvatarDropdownProps> = () => {
  return <SessionProvider>
    <AvatarDropdownContent />
  </SessionProvider>
}

const AvatarDropdownContent: React.FC<AvatarDropdownProps> = () => {

  const session = useSession()
  const userImagePath = session.data?.user?.image

  return <Dropdown
    menu={{ items }}
    trigger={["click"]}
    placement="bottomLeft"
  >
    <div onClick={e => e.preventDefault()}>
      <Avatar
        // eslint-disable-next-line @next/next/no-img-element
        src={userImagePath ? <img src={userImagePath} alt='profile' referrerPolicy='no-referrer' /> : undefined}
        icon={<UserOutlined />}
        style={{
          backgroundColor: '#b3b3b3',
          marginLeft: 'auto',
          cursor: 'pointer',
        }}
        size='large'
      />
    </div>
  </Dropdown>
}

export default AvatarDropdown
