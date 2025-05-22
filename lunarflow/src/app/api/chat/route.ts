import {
  streamText,
  tool as createTool,
  Tool,
  createDataStreamResponse,
  DataStreamWriter,
  Message,
  formatDataStreamPart,
} from 'ai';
import { z } from 'zod';
import { model } from './llm';
import { barChart } from './tools/barChart';
import { displayTable } from './tools/table';
import { lineChart } from './tools/lineChart';
import { listWorkflowsAction } from '@/app/actions/workflows';
import { streamWorkflowResults } from './workflow-streaming';
import { agents, runAgent } from './demo-agents';
import { SYSTEM_PROMPT } from './prompts/system';

type ElementOf<T> = T extends Array<infer U> ? U : never;
type AnyPart = ElementOf<Message["parts"]>;
type ToolInvocationUIPart = Extract<
  AnyPart,
  {
    type: "tool-invocation";
  }
>;

const isWorkflowTool = (toolName: string) => {
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\./i;
  return uuidPattern.test(toolName);
}

const runWorkflow = async (dataStream: DataStreamWriter, toolPart: ToolInvocationUIPart, userId: string) => {
  const result: Record<string, string> = {}
  const workflowId = toolPart.toolInvocation.toolName.split('.')[0]
  for await (const agentEvent of streamWorkflowResults(toolPart.toolInvocation.toolCallId, workflowId, userId)) {
    dataStream.writeData(agentEvent);
    if (agentEvent.type === "lunar-component-result" && agentEvent.reasoningChainComponent.output) {
      const reasoning = agentEvent.reasoningChainComponent.reasoningDescription
      const componentResult = agentEvent.reasoningChainComponent.output.content
      result[toolPart.toolInvocation.toolName + '_' + agentEvent.reasoningChainComponent.id] = 'Reasoning: ' + reasoning + '\n Output: ' + componentResult
    } else if (agentEvent.type === "lunar-component-error") {
      result[toolPart.toolInvocation.toolName] = 'ERROR EXECUTING THE AGENT: ' + agentEvent.lunarAgentError?.message
    }
  }
  dataStream.write(formatDataStreamPart('tool_result', { toolCallId: toolPart.toolInvocation.toolCallId, result }));
}

const runSimulation = async (dataStream: DataStreamWriter, toolPart: ToolInvocationUIPart) => {
  const result: Record<string, string> = {}
  const currentAgent = agents.find(agent => agent.agentName.replaceAll(' ', '_') === toolPart.toolInvocation.toolName)
  if (!currentAgent) {
    dataStream.write(formatDataStreamPart('tool_result', { toolCallId: toolPart.toolInvocation.toolCallId, result: { error: 'Agent not found' } }))
    return
  }
  for await (const agentEvent of runAgent(currentAgent, toolPart.toolInvocation.toolCallId)) {
    dataStream.writeData(agentEvent);
    if (agentEvent.type === "lunar-component-result" && agentEvent.reasoningChainComponent.output) {
      const reasoning = agentEvent.reasoningChainComponent.reasoningDescription
      const componentResult = agentEvent.reasoningChainComponent.output.content
      result[toolPart.toolInvocation.toolName + '_' + agentEvent.reasoningChainComponent.id] = 'Reasoning: ' + reasoning + '\n Output: ' + componentResult
    }
  }
  dataStream.write(formatDataStreamPart('tool_result', { toolCallId: toolPart.toolInvocation.toolCallId, result }));
}

const getTools = async (userId: string) => {
  const tools: Record<string, Tool> = {}

  for (const agent of agents) {
    const toolName = agent.agentName.replaceAll(' ', '_')
    tools[toolName] = createTool({
      description: `${agent.agentDescription} \n\n IMPORTANT: The results of this tool are automatically shown to the user. Pay attention to the output of the tool and check if there are any errors.`,
      parameters: z.object({}),
    })
  }

  const workflows = await listWorkflowsAction(userId)
  workflows.forEach(workflow => {
    const toolName = `${workflow.id}.${workflow.name}`.replaceAll(' ', '_').substring(0, 64)
    tools[toolName] = createTool({
      description: `A tool that can be used to get information about ${workflow.name}. \n\n IMPORTANT: The results of this tool are automatically shown to the user.`,
      parameters: z.object({}),
    })
  })
  tools["barChart"] = barChart
  tools["lineChart"] = lineChart
  tools["displayTable"] = displayTable
  return tools
}

export async function POST(request: Request) {
  const requestJson = await request.json();
  const { messages, data }: { messages: Message[], data: { parameters: any, userId: string } } = requestJson
  const response = createDataStreamResponse({
    execute: async dataStream => {
      const lastMessage = messages[messages.length - 1];
      lastMessage.parts = await Promise.all(
        lastMessage.parts?.map(async part => {
          if (part.type !== 'tool-invocation') {
            return part;
          }
          const toolInvocation = part.toolInvocation;
          if (toolInvocation.state !== 'result') {
            return part;
          }
          switch (toolInvocation.result) {
            case 'No, denied.': {
              const result = 'Error: User denied access to run agent.';
              dataStream.write(
                formatDataStreamPart('tool_result', {
                  toolCallId: toolInvocation.toolCallId,
                  result,
                })
              );
              return {
                ...part,
                toolInvocation: { ...toolInvocation, result }
              };
            }
            case 'Yes, confirmed.': {
              const toolName = part.toolInvocation.toolName;
              if (isWorkflowTool(toolName)) {
                await runWorkflow(dataStream, part, data.userId);
              } else {
                await runSimulation(dataStream, part);
              }
              return part;
            }
            default:
              return part;
          }
        }) ?? []
      );
      const result = streamText({
        model: model,
        system: SYSTEM_PROMPT,
        messages,
        temperature: 0,
        maxSteps: 1,
        tools: await getTools(data.userId),
      });
      result.mergeIntoDataStream(dataStream);
    },
    onError: (error) => {
      console.error('Error in data stream:', error);
      return error instanceof Error ? error.message : String(error);
    }
  });
  return response
}
