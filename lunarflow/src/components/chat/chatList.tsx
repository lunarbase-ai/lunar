// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { Alert, Avatar, Button, List, Skeleton } from "antd"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import { Message } from "ai"
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { ComponentOutput } from "@/models/component/ComponentOutput"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"

interface ChatListProps {
  messages: Message[]
  outputLabels: Record<string, string[]>
}

const ChatList: React.FC<ChatListProps> = ({ messages, outputLabels }) => {

  const router = useRouter()
  const session = useSession()

  const userImage = session.data?.user?.image
  const userName = session.data?.user?.name
  const userEmail = session.data?.user?.email

  return <List
    style={{
      marginTop: 'auto',
    }}
    dataSource={messages}
    renderItem={(message, index) => {
      if (message.toolInvocations) {
        const workflowOutput = message.toolInvocations.map(toolInvocation => {
          const { toolName, toolCallId, state } = toolInvocation;
          if (state === 'result') {
            const { result } = toolInvocation
            const workflowId = toolName.split('_').at(-1)
            if (!workflowId) return <></>
            return Object.keys(result).filter(componentResult => outputLabels[workflowId].includes(componentResult)).map(outputLabel => {
              const output: ComponentOutput | string = result[outputLabel]
              if (typeof output === "string") return <>
                <Alert type="error" message={`There was an error running the workflow! ${output}`} />
                <div style={{ width: '100%', display: 'flex' }}>
                  <Button onClick={() => router.push(`/editor/${workflowId}`)} style={{ marginRight: 'auto', marginLeft: 'auto', marginTop: 8 }}>Open workflow editor</Button>
                </div>
              </>
              if (!output.value) return <></>
              return <GenericOutput
                key={toolCallId + output.key}
                workflowId={workflowId}
                outputDataType={output.dataType}
                content={output.value}
              />
            })
          } else {
            return (
              <div key={toolCallId}>
                <div className='h-[300px] m-4'>
                  <Skeleton active />
                </div>
              </div>
            );
          }
        })
        return <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.role === 'user' ? userImage : LunarImage.src} />}
            title={message.role === 'user' ? userName ?? userEmail : 'Lunar'}
            description={workflowOutput}
          />
        </List.Item>
      }

      return <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.role === 'user' ? userImage : LunarImage.src} />}
            title={message.role === 'user' ? userName ?? userEmail : 'Lunar'}
            description={<ReactMarkdown>{message.content}</ReactMarkdown>}
          />
        </List.Item>
      </>
    }}
  />
}

export default ChatList
