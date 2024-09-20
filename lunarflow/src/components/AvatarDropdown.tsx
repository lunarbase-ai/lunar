// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'

import { Avatar, Dropdown, MenuProps } from "antd"
import { Session } from "next-auth"
import { signOut } from "next-auth/react"

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

interface AvatarDropdownProps {
  session: Session | null
}

const AvatarDropdown: React.FC<AvatarDropdownProps> = ({ session }) => {
  return <Dropdown
    menu={{ items }}
    trigger={["click"]}
    placement="bottomLeft"
  >
    <div onClick={e => e.preventDefault()}>
      <Avatar
        // eslint-disable-next-line @next/next/no-img-element
        src={<img src={session?.user?.image ?? ''} alt='profile' referrerPolicy='no-referrer' />}
        style={{
          marginLeft: 'auto',
          cursor: 'pointer',
        }}
        size='large'
      />
    </div>
  </Dropdown>
}

export default AvatarDropdown
