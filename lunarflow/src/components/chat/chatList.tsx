"use client"
import { Avatar, List, Skeleton, Typography } from "antd"
import { Session } from "next-auth"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import { Message } from "ai"
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { ComponentOutput } from "@/models/component/ComponentOutput"

interface ChatListProps {
  messages: Message[]
  session: Session
  outputLabels: Record<string, string[]>
}

const ChatList: React.FC<ChatListProps> = ({ messages, session, outputLabels }) => {

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
              const output: ComponentOutput = result[outputLabel]
              if (!output.value) return <></>
              console.log(">>>>", output)
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
                {toolName === 'barChart' ? (
                  <div className='h-[300px] m-4'>
                    <Skeleton active />
                  </div>
                ) : null}
              </div>
            );
          }
        })
        return <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.role === 'user' ? session.user?.image : LunarImage.src} />}
            title={message.role === 'user' ? session.user?.name ?? session.user?.email : 'Lunar'}
            description={workflowOutput}
          />
        </List.Item>
      }

      return <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.role === 'user' ? session.user?.image : LunarImage.src} />}
            title={message.role === 'user' ? session.user?.name ?? session.user?.email : 'Lunar'}
            description={<ReactMarkdown>{message.content}</ReactMarkdown>}
          />
        </List.Item>
      </>
    }}
  />
}

export default ChatList
