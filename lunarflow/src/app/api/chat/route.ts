import { streamText, tool as createTool, Tool, createDataStreamResponse, tool, DataStreamWriter } from 'ai';
import { z } from 'zod';
import _ from 'lodash'
import { model } from './llm';
import { cytokineCRSAgent, normalizedDbAgent, wikipediaAgent } from './workflow-streaming/mockedAgents';
import { LunarAgent, LunarComponentInvocationEvent, LunarComponentResultEvent } from '@/app/api/chat/types';

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
  for (let i = 0; i < agent.reasoningChain.length; i++) {
    const componentInvocation: LunarComponentInvocationEvent = {
      type: 'lunar-component-invocation',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: null
      }
    }
    yield componentInvocation
    await new Promise(r => setTimeout(r, agent.reasoningChain[i].executionTime * 1000)); // simulate delay
    const componentResult: LunarComponentResultEvent = {
      type: 'lunar-component-result',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: agent.reasoningChain[i].output,
      }
    }
    yield componentResult
  }
}

export async function POST(request: Request) {
  const { messages, data } = await request.json();

  const workflowToolDataRecord = data.parameters as Record<string, WorkflowToolData>

  const getTools = (dataStream: DataStreamWriter) => {
    const tools: Record<string, Tool> = {}
    const agents = [wikipediaAgent, cytokineCRSAgent, normalizedDbAgent]
    for (const agent of agents) {
      const toolName = agent.agentName.replaceAll(' ', '_')
      tools[toolName] = createTool({
        description: agent.agentDescription,
        parameters: z.object({
          text: z.string().describe("The input text for the agent."),
        }),
        execute: async function (args, { toolCallId }) {
          const result: Record<string, string> = {}
          for await (const agentEvent of runAgent(agent, toolCallId)) {
            dataStream.writeData(agentEvent);
            if (agentEvent.reasoningChainComponent.output) {
              const componentResult = agentEvent.reasoningChainComponent.output.content
              result[toolName + '_' + agentEvent.reasoningChainComponent.id] = componentResult
            }
          }
          console.log(">>>RESULT", result, toolName)
          return result
        }
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
