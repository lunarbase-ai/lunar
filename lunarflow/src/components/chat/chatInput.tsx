// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { Input } from "antd"
import SendButton from "../buttons/SendButton"
import { useState } from "react"

interface ChatInputProps {
  onSubmit: (message: string) => Promise<void>
}

const ChatInput: React.FC<ChatInputProps> = ({ onSubmit }) => {

  const [value, setValue] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  const handleSubmit = async () => {
    setLoading(true)
    setValue('')
    await onSubmit(value)
    setLoading(false)
  }

  return <div style={{
    position: 'sticky',
    zIndex: 10,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 16,
    bottom: 0,
    right: 0,
    left: 0,
    width: '100%',
    backgroundColor: '#fff'
  }}>
    <Input.TextArea
      value={value}
      onChange={(event) => setValue(event.target.value)}
      style={{
        borderRadius: 27,
        padding: '14px 22px',
      }}
      placeholder='Ask something to Lunar'
      variant='filled'
      size='large'
      disabled={loading}
      autoSize
    />
    <SendButton onSubmit={handleSubmit} value={value} />
  </div>
}

export default ChatInput
