import { tool as createTool } from 'ai';
import { z } from 'zod';

export const displayTable = createTool({
  description: "Display the data in a table format. When you call it, it renders the table directly, so no need for further reference. Use this when the user asks to display data in tabular format, such as a list of information organized into rows and columns.",
  parameters: z.object({
    headers: z.string().array(),
    rows: z.array(z.array(z.union([z.string(), z.number(), z.null()]))),
  }),
  execute: async function (parameters) {
    return parameters;
  },
});