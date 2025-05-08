"use client"
import { ToolInvocation } from "ai"
import Button from "../buttons/Button"
import Icon, { CaretRightOutlined } from "@ant-design/icons"
import { Typography } from "antd"
import { ReasoningTypeIcons } from "./chatIcons"
import { ReasoningType } from "@/app/api/chat/types"
import { iconStyle } from "./icons"
import { litReviewAgent } from "@/app/api/chat/mocked/lit-review.agent"
import { bioMarkersAgent } from "@/app/api/chat/mocked/bio-markers.agent"
import AgentInputs from "./agentInputs"
import { grantFinderAgent } from "@/app/api/chat/mocked/grant-finder"
import { normalizedDbAgent } from "@/app/api/chat/mocked/normalizedDBAgent"
import { simulationAgent } from "@/app/api/chat/mocked/simulation.agent"

const { Text, Title } = Typography

type ChatAgentRunConfirmationProps = {
  userId: string
  toolInvocation: ToolInvocation
  addToolResult: ({ toolCallId, result, }: {
    toolCallId: string;
    result: any;
  }) => void
}

const ChatAgentRunConfirmation: React.FC<ChatAgentRunConfirmationProps> = ({
  userId,
  toolInvocation,
  addToolResult,
}) => {
  const { toolCallId } = toolInvocation
  const { toolName } = toolInvocation
  const formattedToolName = toolName.replaceAll("_", " ")
  const ReasoningIcon = ReasoningTypeIcons[ReasoningType.DecomposingProblem]
  return <div style={{ display: 'flex', flexDirection: 'column' }}>
    <div>
      <div style={{ display: 'flex' }}>
        <div style={{ marginRight: 16 }}>
          <Icon style={iconStyle} component={() => <ReasoningIcon fill="#279bce" />} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Text style={{ fontWeight: 600, textTransform: 'uppercase', fontSize: 12, marginBottom: 4 }}>Decomposing Reasoning</Text>
          <Text style={{ fontWeight: 400, fontSize: 14, marginBottom: 4 }}>Selecting specialist agent and decomposing reasoning...</Text>
        </div>
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div>
          <Title level={5} style={{ marginTop: 16 }}>{formattedToolName}</Title>
        </div>

      </div>
    </div>
    <AgentInputs formattedToolName={formattedToolName} agents={[litReviewAgent, bioMarkersAgent, grantFinderAgent, normalizedDbAgent, simulationAgent]} />
    <div style={{
      display: 'flex',
      gap: 8,
      marginTop: 16
    }}>
      <Button style={{ marginLeft: 'auto' }}>
        Cancel
      </Button>
      <Button
        type="primary"
        onClick={() => addToolResult({
          toolCallId,
          result: 'Yes, confirmed.',
        })}
        icon={<CaretRightOutlined />}
        iconPosition="end"
      >
        Run
      </Button>
    </div>
  </div>
}

export default ChatAgentRunConfirmation
