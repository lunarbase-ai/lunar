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
    backgroundColor: '#fff'
  }}>
    <Input.TextArea
      value={input}
      onChange={handleInputChange}
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
    <SendButton
      onSubmit={handleSubmit}
      value={input}
      loading={loading}
    />
  </div>
}

export default ChatInput
