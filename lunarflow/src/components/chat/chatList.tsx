// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { List } from "antd"
import { Message } from "ai"
import "./chat.css"
import { ReactNode } from "react"

interface ChatListProps {
  messages: Message[]
  outputLabels: Record<string, string[]>
  renderItem: (message: Message, index: number) => ReactNode
}

const ChatList: React.FC<ChatListProps> = ({ messages, renderItem }) => {
  return <List
    style={{
      marginTop: 'auto',
      display: 'flex',
      flexDirection: 'column',
    }}
    dataSource={messages}
    renderItem={
      (message, index) => <List.Item style={message.role === 'user' ? { alignSelf: 'end' } : {}}>
        <List.Item.Meta
          description={renderItem(message, index)}
        />
      </List.Item>
    }
    locale={{ emptyText: <></> }}
  />
}

export default ChatList
