import { ComponentModel } from "@/models/component/ComponentModel";
import { LunarAgentEvent, ReasoningType } from "../types";

interface WorkflowEvent {
  workflow_id: string
  outputs: Record<string, string | ComponentModel>
}

export async function* streamWorkflowResults(toolCallId: string, workflowId: string, userId: string) {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_LUNARVERSE_ADDRESS}/workflow/stream?workflow_id=${workflowId}&user_id=${userId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ inputs: [] }),
    });
    if (!response.ok || !response.body) {
      throw new Error(`Streaming failed: ${response.status}`);
    }
    const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      console.log('>>>value', value);
      if (done) break;
      if (!value) continue;
      buffer += value;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const jsonValue = JSON.parse(line) as WorkflowEvent;
          if (Object.keys(jsonValue.outputs).length === 0) continue;
          let previousOutput: Record<string, ComponentModel | string> = {};
          let newOutputs: Record<string, ComponentModel | string> = {};
          for (const key of Object.keys(jsonValue.outputs)) {
            if (!previousOutput[key]) {
              const output = jsonValue.outputs[key] as string | ComponentModel;
              newOutputs[key] = output;
              previousOutput[key] = output;
            }
          }

          for (const key of Object.keys(newOutputs)) {
            const output = newOutputs[key] as string | ComponentModel;
            if (typeof output === 'string') {
              const agentErrorEvent: LunarAgentEvent = {
                type: 'lunar-component-error',
                toolCallId: toolCallId,
                lunarAgentError: {
                  message: output,
                }
              };
              yield agentErrorEvent;
              continue;
            }
            const invocationAgentEvent: LunarAgentEvent = {
              type: 'lunar-component-invocation',
              toolCallId: toolCallId,
              reasoningChainComponent: {
                id: jsonValue.workflow_id,
                reasoningDescription: output.name,
                output: null,
                executionTime: 0,
                reasoningType: 'Lunar component',
                reasoningTypeIcon: ReasoningType.ReasoningOverFacts,
              }
            };
            yield invocationAgentEvent;
            const agentEvent: LunarAgentEvent = {
              type: 'lunar-component-result',
              toolCallId: toolCallId,
              reasoningChainComponent: {
                id: jsonValue.workflow_id,
                reasoningDescription: output.name,
                output: {
                  type: output.output.dataType,
                  content: output.output.value
                },
                executionTime: 0,
                reasoningType: 'workflow',
                reasoningTypeIcon: ReasoningType.ReasoningOverFacts,
              }
            };
            yield agentEvent;
          }
        } catch (e) {
          console.error('Error parsing JSON:', e);
          continue;
        }
      }
    }
  } catch (e) {
    console.error('Stream error:', e);
  }
}
