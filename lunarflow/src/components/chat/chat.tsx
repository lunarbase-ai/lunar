// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import ChatInput from "./chatInput"
import ChatList from "./chatList"
import { useState } from "react"
import ChatHeader from "./chatHeader"
import { WorkflowReference } from "@/models/Workflow"
import { SessionProvider } from "next-auth/react"
import { useChat } from 'ai/react';
import api from "@/app/api/lunarverse"
import { useUserId } from "@/hooks/useUserId"

interface ChatProps {
  workflows: WorkflowReference[]
}

const Chat: React.FC<ChatProps> = (props) => {
  return <SessionProvider>
    <ChatContent {...props} />
  </SessionProvider>
}

const ChatContent: React.FC<ChatProps> = ({ workflows }) => {
  const userId = useUserId()
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
  const [selectedWorkflowIds, setSelectedWorkflowIds] = useState<string[]>([])
  const [outputLabelsById, setOutputLabelsById] = useState<Record<string, string[]>>({})

  const getWorkflowParametersAndSubmit = async (e: any) => {
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
      <ChatHeader workflows={workflows} setSelectedWorkflowIds={setSelectedWorkflowIds} selectedWorkflowIds={selectedWorkflowIds} />
      <ChatList messages={messages} outputLabels={outputLabelsById} />
      <ChatInput
        handleSubmit={getWorkflowParametersAndSubmit}
        input={input}
        handleInputChange={handleInputChange}
        loading={isLoading}
      />
    </SessionProvider>
  </>
}

export default Chat

