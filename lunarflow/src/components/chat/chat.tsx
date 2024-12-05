// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { Message } from "@/models/chat/message"
import ChatInput from "./chatInput"
import ChatList from "./chatList"
import { useState } from "react"
import ChatHeader from "./chatHeader"
import { WorkflowReference } from "@/models/Workflow"
import { sendMessageAction } from "@/app/actions/chat"

interface ChatProps {
  workflows: WorkflowReference[]
}

const Chat: React.FC<ChatProps> = ({
  workflows,
}) => {

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
    const response = await sendMessageAction(message, selectedWorkflowIds)
    const responseMessage: Message = {
      content: response.chatResult.chat_history.findLast(message => message.name === "Assistant")?.content ?? "Sorry, there was a problem generating a response for your message",
      type: 'assistant',
      workflows_output: response.workflowOutput
    }
    messagesCopy.push(responseMessage)
    setMessages([...messagesCopy])
  }

  return <>
    <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} />
    <ChatList
      messages={messages}
    />
    <ChatInput onSubmit={pushMessage} />
  </>
}

export default Chat
