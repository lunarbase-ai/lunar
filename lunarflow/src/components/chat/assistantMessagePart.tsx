import { Divider } from "antd";
import MarkdownOutput from "../io/MarkdownOutput/MarkdownOutput";
import { LunarAgentEvent } from "@/app/api/chat/types";
import { Message } from "ai";
import ChatAgentRunConfirmation from "./chatAgentRunConfirmation";
import AgentDataItem from "./agentDataItem";

type MessagePart = NonNullable<Message['parts']>[number];

interface AssistantMessagePartProps {
  messagePart: MessagePart
  userId: string
  index: number
  addToolResult: ({ toolCallId, result, }: {
    toolCallId: string;
    result: any;
  }) => void
  agentData?: LunarAgentEvent[]
}

const AssistantMessagePart: React.FC<AssistantMessagePartProps> = ({
  messagePart,
  userId,
  addToolResult,
  agentData,
  index
}) => {
  switch (messagePart.type) {
    case 'step-start':
      return index !== 0 ? <Divider></Divider> : <div style={{ marginTop: 16 }}></div>
    case 'text':
      return <MarkdownOutput content={messagePart.text} />
    case 'tool-invocation':
      const { toolCallId, state, args } = messagePart.toolInvocation;
      if (state === 'call') return <ChatAgentRunConfirmation
        userId={userId}
        toolInvocation={messagePart.toolInvocation}
        addToolResult={addToolResult}
      />
      const agentDataItems = agentData?.filter(agent => agent.toolCallId === toolCallId)
      return <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }} key={toolCallId}>
        {agentDataItems?.map((agentDataItem, index) => {
          const agentInvocationItemsLength = agentDataItems.length
          return <AgentDataItem
            event={agentDataItem}
            index={index}
            numberOfEvents={agentInvocationItemsLength}
            toolCallId={toolCallId}
          />
        })}
      </div>
    default:
      console.error('Unknown part type:', messagePart.type, messagePart)
  }
}

export default AssistantMessagePart
