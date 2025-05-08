import { LunarAgent } from "@/app/api/chat/types";
import GenericInput from "../io/GenericInput/GenericInput";
import { Typography } from "antd";
import { useState } from "react";

interface AgentInputsProps {
  formattedToolName: string;
  agents: LunarAgent[];
}

const { Text } = Typography

const AgentInputs: React.FC<AgentInputsProps> = ({ formattedToolName, agents }) => {
  const [inputValue, setInputValue] = useState<Record<string, string>>({})
  const activeAgent = agents.find(agent => formattedToolName === agent.agentName);
  if (!activeAgent) return null;
  return (
    <div style={{ marginTop: 16 }}>
      {activeAgent.inputs.map(({ name, dataType }, index) => (
        <div style={{ marginBottom: 16 }}>
          <Text>{name}</Text>
          <GenericInput
            key={name || index}
            inputKey={name}
            value={inputValue[name] ?? ""}
            inputType={dataType}
            onInputChange={(inputKey, newValue) => {
              setInputValue(prev => ({
                ...prev,
                [inputKey]: newValue,
              }));
            }}
            setParameters={() => { }}
          />
        </div>
      ))}
    </div>
  );
};

export default AgentInputs;
