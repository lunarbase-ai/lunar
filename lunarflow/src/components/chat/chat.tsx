"use client"
import { Message } from "@/models/chat/message"
import ChatInput from "./chatInput"
import ChatList from "./chatList"
import { Session } from "next-auth"
import { useState } from "react"
import ChatHeader from "./chatHeader"
import { WorkflowReference } from "@/models/Workflow"
import { ChatResponse } from "@/models/chat/chat"
import { SessionProvider } from "next-auth/react"

interface ChatProps {
  session: Session
  onSubmit: (message: string, workflowIds: string[]) => Promise<ChatResponse>
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
    const responseMessage: Message = {
      content: response.chatResult.chat_history.findLast(message => message.name === "Assistant")?.content ?? "Sorry, there was a problem generating a response for your message",
      type: 'assistant',
      workflows_output: response.workflowOutput
    }
    messagesCopy.push(responseMessage)
    setMessages([...messagesCopy])
  }

  return <>
    <SessionProvider>
      <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} />
      <ChatList messages={messages} session={session} />
      <ChatInput onSubmit={pushMessage} />
    </SessionProvider>
  </>
}

export default Chat
