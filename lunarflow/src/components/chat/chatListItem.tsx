'use client'
import { ReactNode } from "react"

interface ChatListItemProps {
  userMessage: ReactNode
  assistantMessage: ReactNode
  role: string
}

const ChatListItem: React.FC<ChatListItemProps> = ({
  userMessage,
  assistantMessage,
  role,
}) => {
  return <>
    {(role === 'user')
      ? userMessage
      : assistantMessage}
  </>
}

export default ChatListItem
