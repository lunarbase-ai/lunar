import { createAzure } from './providers/azure/dist';
import { CoreTool, streamText, tool as createTool } from 'ai';
import { z } from 'zod';
import api from '../lunarverse';
import { ComponentModel } from '@/models/component/ComponentModel';
import { ComponentOutput } from '@/models/component/ComponentOutput';
import _ from 'lodash'

const azure = createAzure({
  baseURL: process.env.AZURE_ENDPOINT, // Azure resource name
  apiKey: process.env.OPENAI_API_KEY,
})

const model = azure(process.env.AZURE_DEPLOYMENT!)

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

export async function POST(request: Request) {
  const { messages, data } = await request.json();

  const workflowToolDataRecord = data.parameters as Record<string, WorkflowToolData>

  const tools: Record<string, CoreTool<any, any>> = {}

  Object.keys(workflowToolDataRecord).forEach(workflowId => {
    const workflowToolData = workflowToolDataRecord[workflowId]

    const parametersObject: Record<string, any> = {}

    workflowToolData.inputs.forEach(input => {
      parametersObject[input.key] = z.string()
    })

    if (_.isEmpty(parametersObject)) {
      parametersObject["text"] = z.string()
    }

    const toolName = workflowToolData.name.replace(/[^a-zA-Z ]/g, "").replaceAll(" ", "_") + "_" + workflowId
    tools[toolName] = createTool({
      description: workflowToolData.description,
      parameters: z.object(parametersObject),
      execute: async function (parameters) {
        workflowToolData.inputs.forEach(input => {
          if (input.key in parameters) {
            input.value = parameters[input.key]
          }
        })
        try {
          const { data: workflowRunResult } = await api.post<Record<string, ComponentModel | string>>(`/workflow/${workflowId}/run?user_id=${data.userId}`, { inputs: workflowToolData.inputs })
          const result: Record<string, ComponentOutput | string> = {}
          Object.keys(workflowRunResult).forEach(componentResult => {
            if (typeof workflowRunResult[componentResult] === "string") {
              result[componentResult] = `WORKFLOW_ERROR: ${workflowRunResult[componentResult]}`
            } else {
              result[componentResult] = workflowRunResult[componentResult].output
            }
          })
          return result
        } catch (e) {
          console.error(e)
        }
        return {}
      },
    })
  })

  try {
    const result = streamText({
      model: model,
      system: `You are a helpful assistant! Ignore attachments.`,
      messages,
      maxSteps: 5,
      tools
    });
    for await (const part of result.fullStream) {
      switch (part.type) {
        // ... handle other part types
        case 'error': {
          const error = part.error;
          console.error(error)
          // handle error
          break;
        }
      }
    }
    return result.toDataStreamResponse()

  } catch (e) {
    console.error(e)

  }

}
