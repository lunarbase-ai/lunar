// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { Input } from "antd"
import SendButton from "../buttons/SendButton"
import { ChatRequestOptions } from "ai"

interface ChatInputProps {
  handleSubmit: (event?: {
    preventDefault?: () => void;
  }, chatRequestOptions?: ChatRequestOptions) => void
  input: string
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLTextAreaElement>) => void
  loading: boolean
}

const ChatInput: React.FC<ChatInputProps> = ({
  handleSubmit,
  input,
  handleInputChange,
  loading
}) => {

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
    backgroundColor: '#fff',
    overflow: 'hidden',
  }}>
    <Input.TextArea
      value={input}
      onChange={handleInputChange}
      style={{
        borderRadius: 27,
        padding: '14px 22px',
        height: 55,
      }}
      placeholder='Ask something to Lunar'
      variant='filled'
      size='large'
      disabled={loading}
      autoSize
    />
    <SendButton
      onSubmit={handleSubmit}
      value={input}
      loading={loading}
    />
  </div>
}

export default ChatInput
