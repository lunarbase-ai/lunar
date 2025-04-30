// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { Alert, Divider, List, Spin, Typography } from "antd"
import { Message } from "ai"
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { useSession } from "next-auth/react"
import "./chat.css"
import { LunarAgentEvent } from "../../app/api/chat/types"
import Icon, { LoadingOutlined } from "@ant-design/icons"
import { ReasoningTypeIcons } from "./chatIcons"
import { CSSProperties } from "react"
import MarkdownOutput from "../io/MarkdownOutput/MarkdownOutput"

interface ChatListProps {
  messages: Message[]
  outputLabels: Record<string, string[]>
  agentData?: LunarAgentEvent[]
}

const iconStyle: CSSProperties = { fontSize: 40 }

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];
  if (hrs > 0) parts.push(`${hrs} hour${hrs !== 1 ? 's' : ''}`);
  if (mins > 0) parts.push(`${mins} minute${mins !== 1 ? 's' : ''}`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs} second${secs !== 1 ? 's' : ''}`);

  return parts.join(' ');
}


const ChatList: React.FC<ChatListProps> = ({ messages, outputLabels, agentData }) => {

  const session = useSession()

  const userImage = session.data?.user?.image
  const userName = session.data?.user?.name
  const userEmail = session.data?.user?.email

  const { Text } = Typography

  return <List
    style={{
      marginTop: 'auto',
      display: 'flex',
      flexDirection: 'column',
    }}
    dataSource={messages}
    renderItem={(message, index) => {
      return <>
        <List.Item key={index} style={message.role === 'user' ? { alignSelf: 'end' } : {}}>
          <List.Item.Meta
            description={message.parts?.map((part, index) => {
              if (message.role === 'user') {
                return <div className="lunar-user-message" style={{
                  backgroundColor: '#1E3257',
                  paddingTop: 8,
                  paddingBottom: 8,
                  paddingLeft: 16,
                  paddingRight: 16,
                  borderRadius: 8,
                  maxWidth: '90%',
                  alignSelf: 'end',
                  display: 'inline-block',
                  position: 'relative'
                }} key={index}>
                  {message.parts?.map(part => part.type === "text" ? <p style={{ color: '#fff' }}>{part.text}</p> : <></>)}
                </div>
              }
              switch (part.type) {
                case 'step-start':
                  return index !== 0 ? <Divider key={index}></Divider> : <div style={{ marginTop: 16 }}></div>
                case 'text':
                  return <MarkdownOutput content={part.text} />
                case 'tool-invocation':
                  const { toolCallId, state } = part.toolInvocation;
                  if (!agentData || agentData.length === 0) {
                    if (state === 'call' || state === 'partial-call') {
                      return <div style={{ width: '100%', display: 'flex', marginBottom: 8 }} key={toolCallId}>
                        <div style={{ marginRight: 8 }}>
                          <Spin indicator={<LoadingOutlined spin />} size="small" />
                        </div>
                        <Text>Calling agent...</Text>
                      </div>
                    }
                    return <></>
                  }
                  const agentDataItems = agentData.filter(agent => agent.toolCallId === toolCallId)
                  return <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }} key={toolCallId}>
                    {agentDataItems.map((agentDataItem, index) => {
                      const agentDataItemsLength = agentDataItems.length
                      if (agentDataItem.type === 'lunar-component-invocation') {
                        return <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <div style={{ display: 'flex' }}>
                            <div style={{ marginRight: 16 }}>
                              {
                                index + 1 === agentDataItemsLength && state !== 'result' ?
                                  <Icon className="pulse-icon" style={iconStyle} component={ReasoningTypeIcons[agentDataItem.reasoningChainComponent.reasoningType]} /> :
                                  <Icon style={iconStyle} component={ReasoningTypeIcons[agentDataItem.reasoningChainComponent.reasoningType]} />
                              }
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                              <Text style={{ fontWeight: 600, textTransform: 'uppercase', fontSize: 12, marginBottom: 4 }}>{agentDataItem.reasoningChainComponent.reasoningType}</Text>
                              <Text style={{ fontWeight: 400, fontSize: 14, marginBottom: 4 }}>{agentDataItem.reasoningChainComponent.reasoningDescription}</Text>
                            </div>
                          </div>
                        </div>
                      } else if (agentDataItem.type === 'lunar-component-result') {
                        const componentOutput = agentDataItem.reasoningChainComponent.output
                        return <div style={{ marginLeft: 56, marginBottom: 72 }} key={toolCallId + index}>
                          <GenericOutput
                            key={toolCallId + index}
                            workflowId={toolCallId}
                            outputDataType={componentOutput.type}
                            content={componentOutput.content}
                          />
                        </div>
                      } else if (agentDataItem.type === 'lunar-component-error') {
                        return <Alert type="error" message={agentDataItem.lunarAgentError.message} />
                      } else if (agentDataItem.type === 'lunar-agent-result') {
                        return <div style={{ marginBottom: 48 }} key={toolCallId + index}>
                          <p style={{ overflowWrap: 'break-word', userSelect: 'text', cursor: 'text' }}>
                            Reasoning ran in {formatTime(agentDataItem.runningTime)}
                          </p>
                          <p style={{ overflowWrap: 'break-word', userSelect: 'text', cursor: 'text' }}>
                            Estimated baseline for doing it manually: {formatTime(agentDataItem.manualtime)}
                          </p>
                        </div>
                      }
                    })}
                  </div>
                default:
                  console.error('Unknown part type:', part.type, part)
              }
            })}
          />
        </List.Item>
      </>
    }}
    locale={{ emptyText: <></> }}
  />
}

export default ChatList
