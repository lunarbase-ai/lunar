// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { Input } from "antd"
import SendButton from "../buttons/SendButton"
import { ChatRequestOptions } from "ai"
import Button from "../buttons/Button"

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
    bottom: 0,
    zIndex: 10,
    right: 0,
    left: 0,
    width: '100%',
    backgroundColor: '#fff',
  }}>
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      padding: 16,
      width: '100%',
      backgroundColor: '#fff',
      overflow: 'hidden',
      boxShadow: '0px 4px 20px rgba(30, 50, 87, 0.1)',
      borderRadius: 10,
      marginBottom: 40
    }}>
      <Input.TextArea
        value={input}
        onChange={handleInputChange}
        style={{
          border: 0,
          background: 'transparent'
        }}
        placeholder='Ask something to Lunar'
        variant='filled'
        size='large'
        disabled={loading}
        autoSize
      />
      <div style={{ display: 'flex', alignItems: 'center', marginTop: 4, gap: 8 }}>
        <Button style={{ marginLeft: 'auto' }}>
          New chat
        </Button>
        <SendButton
          onSubmit={handleSubmit}
          value={input}
          loading={loading}
        />
      </div>
    </div>
  </div>
}

export default ChatInput
