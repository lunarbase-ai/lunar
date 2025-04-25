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
  const { messages, input, handleInputChange, handleSubmit, status, data } = useChat({ experimental_throttle: 50 });
  const [selectedWorkflowIds, setSelectedWorkflowIds] = useState<string[]>([])
  const [outputLabelsById, setOutputLabelsById] = useState<Record<string, string[]>>({})
  const getWorkflowParametersAndSubmit = async (e: any) => {
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
  return <>
    <SessionProvider>
      {/* <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} /> */}
      <ChatList messages={messages} outputLabels={outputLabelsById} agentData={data as unknown as LunarAgentEvent[] | undefined} />
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

