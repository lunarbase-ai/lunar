// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import ChatInput from "./chatInput"
import ChatList from "./chatList"
import { useState } from "react"
import { WorkflowReference } from "@/models/Workflow"
import { SessionProvider } from "next-auth/react"
import { useChat } from "@ai-sdk/react"
import api from "@/app/api/lunarverse"
import { useUserId } from "@/hooks/useUserId"
import { LunarAgentEvent } from "../../app/api/chat/types"
import { Typography } from "antd"
import ChatListItem from "./chatListItem"
import UserMessage from "./userMessage"
import AssistantMessage from "./assistantMessage"
import AssistantMessagePart from "./assistantMessagePart"

const { Title } = Typography

interface ChatProps {
  workflows: WorkflowReference[]
}

const Chat: React.FC<ChatProps> = (props) => {
  return <SessionProvider>
    <ChatContent {...props} />
  </SessionProvider>
}

const scrollToBottom = () => {
  setTimeout(() => {
    const scroller = document.getElementById('scroller');
    scroller?.scrollTo({
      top: scroller.scrollHeight,
      behavior: 'smooth'
    });
  }, 50);
}

const ChatContent: React.FC<ChatProps> = ({ workflows }) => {
  const userId = useUserId()
  const { messages, input, handleInputChange, handleSubmit, addToolResult, status, data } = useChat({
    experimental_throttle: 50,
    experimental_prepareRequestBody: ({ messages }) => {
      return { messages, data: { userId: userId ?? '' } }
    }
  });
  const [selectedWorkflowIds, setSelectedWorkflowIds] = useState<string[]>([])
  const [outputLabelsById, setOutputLabelsById] = useState<Record<string, string[]>>({})

  const getWorkflowParametersAndSubmit = async (e: any) => {
    if (!userId) return;
    scrollToBottom()
    const outputLabelsByIdCopy = { ...outputLabelsById }
    const parameters: Record<string, any> = {}
    await Promise.all(selectedWorkflowIds.map(async (selectedWorkflowId) => {
      const { data: workflowParameters } = await api.get(`/workflow/${selectedWorkflowId}/inputs?user_id=${userId}`)
      parameters[selectedWorkflowId] = workflowParameters
      const { data: workflowOutputs } = await api.get<string[]>(`/workflow/${selectedWorkflowId}/outputs?user_id=${userId}`)
      outputLabelsByIdCopy[selectedWorkflowId] = workflowOutputs
    }))
    setOutputLabelsById(outputLabelsByIdCopy)
    try {
      handleSubmit(e, { data: { parameters, userId } })
    } catch (e) {
      console.error(e)
    }
  }

  if (!userId) return <></>
  return <>
    <SessionProvider>
      {/* <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} /> */}
      {messages.length > 0
        ? <ChatList
          messages={messages}
          outputLabels={outputLabelsById}
          renderItem={(message, index) => <ChatListItem
            userMessage={<UserMessage message={message} />}
            assistantMessage={<AssistantMessage
              messagePartRender={(messagePart, messagePartIndex) => <AssistantMessagePart
                messagePart={messagePart}
                userId={userId ?? ''}
                index={messagePartIndex}
                addToolResult={addToolResult}
                agentData={data as unknown as LunarAgentEvent[] | undefined}
              />}
              message={message}
            />}
            role={message.role}
            key={index}
          />}
        />
        : <Title level={2} style={{ textAlign: 'center', marginTop: '30vh' }}>
          What will we discover today?
        </Title>
      }
      <ChatInput
        handleSubmit={getWorkflowParametersAndSubmit}
        input={input}
        handleInputChange={handleInputChange}
        loading={status === 'submitted' || status === 'streaming'}
      />
    </SessionProvider>
  </>
}

export default Chat

