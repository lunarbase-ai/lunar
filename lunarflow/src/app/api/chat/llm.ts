import { createAzure } from './providers/azure/dist';

const azure = createAzure({
  baseURL: process.env.AZURE_OPENAI_ENDPOINT, // Azure resource name
  apiKey: process.env.AZURE_OPENAI_API_KEY,
})

export const model = azure(process.env.AZURE_OPENAI_DEPLOYMENT!)
