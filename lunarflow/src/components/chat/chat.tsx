"use client"
import { Message } from "@/models/chat/message"
import ChatInput from "./chatInput"
import ChatList from "./chatList"
import { Session } from "next-auth"
import { useState } from "react"
import ChatHeader from "./chatHeader"
import { WorkflowReference } from "@/models/Workflow"

interface ChatProps {
  session: Session
  onSubmit: (message: string, workflowIds: string[]) => Promise<Message>
  workflows: WorkflowReference[]
}

const Chat: React.FC<ChatProps> = ({ onSubmit, session, workflows }) => {

  const [messages, setMessages] = useState<Message[]>([])
  const [selectedWorkflowIds, setSelectedWorkflowIds] = useState<string[]>([])

  const pushMessage = async (message: string) => {
    const messagesCopy = [...messages]
    const userMessage: Message = {
      content: message,
      type: 'human'
    }
    messagesCopy.push(userMessage)
    setMessages(messagesCopy)
    const response = await onSubmit(message, selectedWorkflowIds)
    messagesCopy.push(response)
    setMessages([...messagesCopy])
  }

  return <>
    <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} />
    <ChatList messages={messages} session={session} />
    <ChatInput onSubmit={pushMessage} />
  </>
}

export default Chat
