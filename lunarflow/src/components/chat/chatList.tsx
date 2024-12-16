"use client"
import { Alert, Avatar, Button, List, Skeleton, Typography } from "antd"
import { Session } from "next-auth"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import { Message } from "ai"
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { ComponentOutput } from "@/models/component/ComponentOutput"
import { useRouter } from "next/navigation"

interface ChatListProps {
  messages: Message[]
  session: Session
  outputLabels: Record<string, string[]>
}

const ChatList: React.FC<ChatListProps> = ({ messages, session, outputLabels }) => {

  const router = useRouter()

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
