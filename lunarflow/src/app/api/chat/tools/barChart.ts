import { tool as createTool } from 'ai';
import { z } from 'zod';

export const barChart = createTool({
  description: "Display a bar chart for comparing numerical values across categories. Use this to highlight differences or distributions among groups, such as sales figures by product or performance metrics by team. It is ideal for emphasizing contrasts or comparisons. When you call it, it already renders, so you don't need to reference it later.",
  parameters: z.object({
    labels: z.string().array(),
    datasets: z.object({
      data: z.number().array()
    }).array()
  }),
  execute: async function (parameters) {
    return parameters
  },
});
