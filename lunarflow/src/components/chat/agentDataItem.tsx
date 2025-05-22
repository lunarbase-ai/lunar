import { LunarAgentEvent } from "@/app/api/chat/types"
import { ReasoningTypeIcons } from "./chatIcons";
import Icon from "@ant-design/icons";
import { iconStyle } from "./icons";
import { Alert, Typography } from "antd";
import GenericOutput from "../io/GenericOutput/GenericOutput";
const { Text } = Typography

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

const colors = ['#279bce', '#da3576', '#2436a8', '#e07000', '#3c4b1b']

interface AgentDataItemProps {
  event: LunarAgentEvent
  index: number
  numberOfEvents: number
  toolCallId: string
}

const AgentDataItem: React.FC<AgentDataItemProps> = ({ event, numberOfEvents, index, toolCallId }) => {
  const currentColor = colors[index % colors.length]
  switch (event.type) {
    case 'lunar-component-invocation':
      const ReasoningIcon = ReasoningTypeIcons[event.reasoningChainComponent.reasoningTypeIcon]
      return <div key={toolCallId + index} style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex' }}>
          <div style={{ marginRight: 16 }}>
            {
              index + 1 === numberOfEvents ?
                <Icon className="pulse-icon" style={iconStyle} component={() => <ReasoningIcon fill={currentColor} />} /> :
                <Icon style={iconStyle} component={() => <ReasoningIcon fill={currentColor} />} />
            }
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <Text style={{ fontWeight: 600, textTransform: 'uppercase', fontSize: 12, marginBottom: 4 }}>{event.reasoningChainComponent.reasoningType}</Text>
            <Text style={{ fontWeight: 400, fontSize: 14, marginBottom: 4 }}>{event.reasoningChainComponent.reasoningDescription}</Text>
          </div>
        </div>
      </div>
    case 'lunar-component-result':
      const componentOutput = event.reasoningChainComponent.output
      if (typeof componentOutput === 'string') {
        return <Alert message={componentOutput} type="warning" showIcon closable />
      }
      return <div style={{ marginLeft: 56, marginBottom: 72 }} key={toolCallId + index}>
        <GenericOutput
          key={toolCallId + index}
          workflowId={toolCallId}
          outputDataType={componentOutput.type}
          content={componentOutput.content}
        />
      </div>
    case 'lunar-component-error':
      return <Alert type="error" message={event.lunarAgentError.message} key={toolCallId + index} style={{ marginBottom: 16 }} />
    case 'lunar-agent-result':
      return <div style={{ marginBottom: 48 }} key={toolCallId + index}>
        <p style={{ overflowWrap: 'break-word', userSelect: 'text', cursor: 'text', fontWeight: 600 }}>
          Reasoning ran in {formatTime(event.runningTime)}
        </p>
        <p style={{ overflowWrap: 'break-word', userSelect: 'text', cursor: 'text', fontWeight: 600 }}>
          Estimated baseline for doing it manually: {formatTime(event.manualtime)}
        </p>
      </div>

  }
}

export default AgentDataItem
