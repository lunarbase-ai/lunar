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
import _ from 'lodash'
import { model } from './llm';
import { LunarAgent, LunarAgentEvent } from '@/app/api/chat/types';
import { normalizedDbAgent } from './mocked/normalizedDBAgent';
import { litReviewAgent } from './mocked/lit-review.agent';
import { simulationAgent } from './mocked/simulation.agent';
import { bioMarkersAgent } from './mocked/bio-markers.agent';
import { grantFinderAgent } from './mocked/grant-finder';
import { ComponentOutput } from '@/models/component/ComponentOutput';
import { analyticAgent } from './mocked/analytic-agent';

interface WorkflowInput {
  id: string
  type: string
  key: string
  is_template_variable: boolean
  value: string
}

type ElementOf<T> = T extends Array<infer U> ? U : never;
type AnyPart = ElementOf<Message["parts"]>;
type ToolInvocationUIPart = Extract<
  AnyPart,
  {
    type: "tool-invocation";
  }
>;

interface WorkflowToolData {
  name: string
  description: string
  inputs: WorkflowInput[]
}

const agents = [
  analyticAgent,
  normalizedDbAgent,
  litReviewAgent,
  simulationAgent,
  bioMarkersAgent,
  grantFinderAgent
]

async function* runAgent(agent: LunarAgent, toolCallId: string) {
  let elapsedTime = 0
  for (let i = 0; i < agent.reasoningChain.length; i++) {
    const componentInvocation: LunarAgentEvent = {
      type: 'lunar-component-invocation',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: null
      }
    }
    yield componentInvocation
    await new Promise(r => setTimeout(r, agent.reasoningChain[i].executionTime * 1000)); // simulate delay
    elapsedTime += agent.reasoningChain[i].executionTime
    const componentResult: LunarAgentEvent = {
      type: 'lunar-component-result',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: agent.reasoningChain[i].output,
      }
    }
    yield componentResult
  }
  const reasoningComplete: LunarAgentEvent = {
    type: 'lunar-agent-result',
    toolCallId: toolCallId,
    runningTime: elapsedTime,
    manualtime: agent.manualTime,
  }
  yield reasoningComplete
}

const streamWorkflowResults = async (workflowId: string, userId: string) => {
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
      if (done) break;
      buffer += value;
      let parts = buffer.split(/\r?\n\r?\n/);
      buffer = parts.pop()!; // last partial chunk remains
    }
  } catch (e) {
    console.error(e)
  }
}

const runSimulation = async (dataStream: DataStreamWriter, toolPart: ToolInvocationUIPart) => {
  const result: Record<string, string> = {}
  const currentAgent = agents.find(agent => agent.agentName.replaceAll(' ', '_') === toolPart.toolInvocation.toolName) ?? litReviewAgent
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

export async function POST(request: Request) {
  const requestJson = await request.json();
  const { messages, data }: { messages: Message[], data: { parameters: any, userId: string } } = requestJson
  // const workflowToolDataRecord = data.parameters as Record<string, WorkflowToolData>

  const getTools = (dataStream: DataStreamWriter) => {

    const tools: Record<string, Tool> = {}

    for (const agent of agents) {
      const toolName = agent.agentName.replaceAll(' ', '_')
      tools[toolName] = createTool({
        description: `${agent.agentDescription} \n\n IMPORTANT: The results of this tool are automatically shown to the user.`,
        parameters: z.object({}),
      })
    }

    tools["0613459f-fcbe-4b18-9b3e-f2a14cb15ab6.finance"] = createTool({
      description: `A tool that can be used to get information about Tesla finance. \n\n IMPORTANT: The results of this tool are automatically shown to the user.`,
      parameters: z.object({}),
    })

    return tools
  }

  const response = createDataStreamResponse({
    execute: async dataStream => {
      const lastMessage = messages[messages.length - 1];
      const toolPart = lastMessage.parts?.find(p => p.type === 'tool-invocation' && p.toolInvocation.state === 'result');
      if (toolPart?.type === 'tool-invocation' && toolPart.toolInvocation.state === 'result' && toolPart.toolInvocation.result === 'Yes, confirmed.') {
        await runSimulation(dataStream, toolPart)

        // const workflowId = toolPart.toolInvocation.toolName.split('.').at(0) ?? ''
        // if (workflowId.length > 0) {
        //   await streamWorkflowResults(workflowId, data.userId)
        // } else {
        //   await runSimulation(dataStream, toolPart)
        // }
        return;
      }
      lastMessage.parts = await Promise.all(
        lastMessage.parts?.map(async part => {
          if (part.type !== 'tool-invocation') {
            return part;
          }
          const toolInvocation = part.toolInvocation;
          if (
            toolInvocation.state !== 'result'
          ) {
            return part;
          }
          switch (toolInvocation.result) {
            case 'No, denied.': {
              const result = 'Error: User denied access to run agent.';

              dataStream.write(
                formatDataStreamPart('tool_result', {
                  toolCallId: toolInvocation.toolCallId,
                  result,
                }),
              );
              return { ...part, toolInvocation: { ...toolInvocation, result } };
            }
            default:
              return part;
          }
        }) ?? [],
      )

      const result = streamText({
        model: model,
        system: `You are a helpful assistant! Ignore attachments.`,
        messages,
        temperature: 0,
        maxSteps: 1,
        tools: getTools(dataStream),
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

// execute: async function (parameters) {
//   try {
//     const response = await fetch(`${process.env.NEXT_PUBLIC_LUNARVERSE_ADDRESS}/workflow/stream?workflow_id=0613459f-fcbe-4b18-9b3e-f2a14cb15ab6&user_id=${data.userId}`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({ inputs: [] }),
//     });
//     if (!response.ok || !response.body) {
//       throw new Error(`Streaming failed: ${response.status}`);
//     }
//     const reader = response.body.getReader();
//     const decoder = new TextDecoder("utf-8");
//     let result: Record<string, ComponentOutput | string> = {};
//     let buffer = "";

//     while (true) {
//       const { done, value } = await reader.read();
//       const compResult = decoder.decode(value, { stream: true });
//       console.log(">>>Comp result", compResult)
//       if (done) break;
//     }

//   } catch (e) {
//     console.error(e)
//   }
// },

// const getTools = (dataStream: any) => {
//   const tools: Record<string, Tool> = {}

//   Object.keys(workflowToolDataRecord).forEach(workflowId => {
//     const workflowToolData = workflowToolDataRecord[workflowId]

//     const parametersObject: Record<string, any> = {}

//     workflowToolData.inputs.forEach(input => {
//       parametersObject[input.key] = z.string()
//     })

//     if (_.isEmpty(parametersObject)) {
//       parametersObject["text"] = z.string()
//     }

//     const toolName = workflowToolData.name.replace(/[^a-zA-Z ]/g, "").replaceAll(" ", "_") + "_" + workflowId
//     tools[toolName] = createTool({
//       description: workflowToolData.description,
//       parameters: z.object(parametersObject),
//       execute: async function (parameters) {
//         workflowToolData.inputs.forEach(input => {
//           if (input.key in parameters) {
//             input.value = parameters[input.key]
//           }
//         })
//         try {
// const { data: workflowRunResult } = await api.post<Record<string, ComponentModel | string>>(`/workflow/${workflowId}/run?user_id=${data.userId}`, { inputs: workflowToolData.inputs })
//           const result: Record<string, ComponentOutput | string> = {}
//           Object.keys(workflowRunResult).forEach(componentResultKey => {
//             const componentResult = workflowRunResult[componentResultKey]
//             if (typeof componentResult === "string") {
//               result[componentResultKey] = `WORKFLOW_ERROR: ${componentResult}`
//             } else {
//               result[componentResultKey] = componentResult.output
//             }
//           })
//           return result
//         } catch (e) {
//           console.error(e)
//         }
//         return {}
//       },
//     })
//   })
//   return tools
// }




// execute: async function (args, { toolCallId }) {
//   const result: Record<string, string> = {}
//   for await (const agentEvent of runAgent(agent, toolCallId)) {
//     dataStream.writeData(agentEvent);
//     if (agentEvent.type === "lunar-component-result" && agentEvent.reasoningChainComponent.output) {
//       const reasoning = agentEvent.reasoningChainComponent.reasoningDescription
//       const componentResult = agentEvent.reasoningChainComponent.output.content
//       result[toolName + '_' + agentEvent.reasoningChainComponent.id] = 'Reasoning: ' + reasoning + '\n Output: ' + componentResult
//     }
//   }
//   return result
// },