import { ComponentDataType } from "@/models/component/ComponentModel";

export type LunarAgentInput = {
  name: string;
  dataType: string;
};

export type LunarAgentReasoningComponentOutput = {
  type: ComponentDataType;
  content: string;
}

export type LunarAgentReasoningComponent = {
  id: string;
  reasoningType: string;
  reasoningDescription: string;
  executionTime: number; // in seconds
  output: LunarAgentReasoningComponentOutput;
}


export type LunarAgent = {
  instruction: string;
  agentName: string;
  agentDescription: string;
  inputs: LunarAgentInput[];
  reasoningChain: LunarAgentReasoningComponent[];
  manualTime: number; // in seconds
};

export type LunarAgentError = {
  message: string
}

export type LunarComponentInvocationEvent = {
  type: 'lunar-component-invocation';
  toolCallId: string;
  reasoningChainComponent: Omit<LunarAgentReasoningComponent, 'output'> & { output: null };
};

export type LunarComponentResultEvent = {
  type: 'lunar-component-result';
  toolCallId: string;
  reasoningChainComponent: LunarAgentReasoningComponent;
};

export type LunarComponentErrorEvent = {
  type: 'lunar-component-error';
  toolCallId: string;
  reasoningChainComponent: LunarAgentError;
};

export type LunarAgentEvent =
  | LunarComponentInvocationEvent
  | LunarComponentResultEvent
  | LunarComponentErrorEvent;

