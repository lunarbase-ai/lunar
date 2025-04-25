// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { Alert, Avatar, Divider, List, Spin, Typography } from "antd"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { atomOneLight } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import { Message } from "ai"
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import "./chat.css"
import { LunarAgentEvent } from "../../app/api/chat/types"
import { CheckCircleTwoTone, LoadingOutlined } from "@ant-design/icons"
import remarkGfm from 'remark-gfm'

interface ChatListProps {
  messages: Message[]
  outputLabels: Record<string, string[]>
  agentData?: LunarAgentEvent[]
}

const ChatList: React.FC<ChatListProps> = ({ messages, outputLabels, agentData }) => {

  const router = useRouter()
  const session = useSession()

  const userImage = session.data?.user?.image
  const userName = session.data?.user?.name
  const userEmail = session.data?.user?.email

  const { Text } = Typography

  return <List
    style={{
      marginTop: 'auto',
    }}
    dataSource={messages}
    renderItem={(message, index) => {
      return <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.role === 'user' ? userImage : LunarImage.src} />}
            title={message.role === 'user' ? userName ?? userEmail : 'Lunar'}
            description={message.parts?.map((part, index) => {
              switch (part.type) {
                case 'step-start':
                  return index !== 0 ? <Divider key={index}></Divider> : <div style={{ marginTop: 16 }}></div>
                case 'text':
                  return <ReactMarkdown
                    key={index}
                    components={{
                      code(props) {
                        const { children, className, node, ...rest } = props
                        const match = /language-(\w+)/.exec(className || '')
                        return match ? (
                          <SyntaxHighlighter
                            language={match[1]}
                            style={atomOneLight}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code {...rest} className={className}>
                            {children}
                          </code>
                        )
                      }
                    }}
                    remarkPlugins={[remarkGfm]}
                  >
                    {part.text}
                  </ReactMarkdown>
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
                  return <div style={{ width: '100%', display: 'flex', flexDirection: 'column', marginBottom: 8 }} key={toolCallId}>
                    {agentDataItems.map((agentDataItem, index) => {
                      const agentDataItemsLength = agentDataItems.length
                      if (agentDataItem.type === 'lunar-component-invocation') {
                        return <div style={{ display: 'flex' }}>
                          <div style={{ marginRight: 8 }}>
                            {index + 1 === agentDataItemsLength && state !== 'result' ? <Spin indicator={<LoadingOutlined spin />} size="small" /> : <CheckCircleTwoTone twoToneColor="#52c41a" />
                            }
                          </div>
                          <Text>{agentDataItem.reasoningChainComponent.reasoningDescription}</Text>
                        </div>
                      } else if (agentDataItem.type === 'lunar-component-result') {
                        const componentOutput = agentDataItem.reasoningChainComponent.output
                        return <div style={{ marginTop: 8, marginBottom: 8 }} key={toolCallId + index}>
                          <GenericOutput
                            key={toolCallId + index}
                            workflowId={toolCallId}
                            outputDataType={componentOutput.type}
                            content={componentOutput.content}
                          />
                        </div>
                      } else {
                        return <Alert type="error" message={agentDataItem.reasoningChainComponent.message} />
                      }
                    })}
                  </div>
                // const agentName = toolName.split('_').at(0)
                // const agentId = toolName.split('_').at(-1)
                // if (state === 'result') {
                //   const result = part.toolInvocation.result
                //   if (!agentId) return <></>
                //   console.log(">>>RESULT", result, toolName, outputLabels)
                // return Object.keys(result).filter(componentResult => outputLabels[toolName].includes(componentResult)).map(outputLabel => {
                //   const output: ComponentOutput | string = result[outputLabel]
                //   if (typeof output === "string") return <>
                //     <Alert type="error" message={`There was an error running the agent! ${output}`} />
                //     <div style={{ width: '100%', display: 'flex' }}>
                //       <Button onClick={() => router.push(`/editor/${agentId}`)} style={{ marginRight: 'auto', marginLeft: 'auto', marginTop: 8 }}>Open workflow editor</Button>
                //     </div>
                //   </>
                //   if (!output.value) return <></>
                //   return <div>
                //     <div style={{ width: '100%', display: 'flex', marginBottom: 8 }}>
                //       <Button style={{ marginLeft: 'auto' }} onClick={() => router.push(`/editor/${agentId}`)}>Edit {agentName} agent</Button>
                //     </div>
                //     <GenericOutput
                //       key={toolCallId + output.key}
                //       workflowId={agentId}
                //       outputDataType={output.dataType}
                //       content={output.value}
                //     />
                //   </div>
                // })
                // } else {
                //   return (
                //     <div key={toolCallId}>
                //       <ReactMarkdown key={index}>{`Calling ${agentName}...`}</ReactMarkdown>
                //       <div className='h-[300px] m-4'>
                //         <Skeleton active />
                //       </div>
                //     </div>
                //   );
                // }
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
