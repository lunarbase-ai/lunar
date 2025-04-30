import { streamText, tool as createTool, Tool, createDataStreamResponse, tool, DataStreamWriter } from 'ai';
import { z } from 'zod';
import _ from 'lodash'
import { model } from './llm';
import { LunarAgent, LunarAgentEvent, LunarComponentInvocationEvent, LunarComponentResultEvent } from '@/app/api/chat/types';
import { wikipediaAgent } from './mocked/wikipedia';
import { normalizedDbAgent } from './mocked/normalizedDBAgent';
import { litReviewAgent } from './mocked/lit-review.agent';
import { simulationAgent } from './mocked/simulation.agent';
import { bioMarkersAgent } from './mocked/bio-markers.agent';

interface WorkflowInput {
  id: string
  type: string
  key: string
  is_template_variable: boolean
  value: string
}

interface WorkflowToolData {
  name: string
  description: string
  inputs: WorkflowInput[]
}

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

export async function POST(request: Request) {
  const { messages, data } = await request.json();

  const workflowToolDataRecord = data.parameters as Record<string, WorkflowToolData>

  const getTools = (dataStream: DataStreamWriter) => {
    const tools: Record<string, Tool> = {}
    const agents = [wikipediaAgent, normalizedDbAgent, litReviewAgent, simulationAgent, bioMarkersAgent]
    for (const agent of agents) {
      const toolName = agent.agentName.replaceAll(' ', '_')
      tools[toolName] = createTool({
        description: `${agent.agentDescription} \n\n IMPORTANT: The results of this tool are automatically shown to the user.`,
        parameters: z.object({}),
        execute: async function (args, { toolCallId }) {
          const result: Record<string, string> = {}
          for await (const agentEvent of runAgent(agent, toolCallId)) {
            dataStream.writeData(agentEvent);
            if (agentEvent.type === "lunar-component-result" && agentEvent.reasoningChainComponent.output) {
              const reasoning = agentEvent.reasoningChainComponent.reasoningDescription
              const componentResult = agentEvent.reasoningChainComponent.output.content
              result[toolName + '_' + agentEvent.reasoningChainComponent.id] = 'Reasoning: ' + reasoning + '\n Output: ' + componentResult
            }
          }
          return result
        },
      })
    }
    return tools
  }

  const response = createDataStreamResponse({
    execute: dataStream => {
      const result = streamText({
        model: model,
        system: `You are a helpful assistant! Ignore attachments.`,
        messages,
        temperature: 0,
        maxSteps: 5,
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

  // return result.toDataStreamResponse()

}

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
//           const { data: workflowRunResult } = await api.post<Record<string, ComponentModel | string>>(`/workflow/${workflowId}/run?user_id=${data.userId}`, { inputs: workflowToolData.inputs })
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
