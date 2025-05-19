import { tool as createTool } from 'ai';
import { z } from 'zod';

export const lineChart = createTool({
  description: "Display a line chart for a list of labels and corresponding datasets. Each dataset includes a series of numbers. Use this to visualize trends or time series, such as data that changes over time.",
  parameters: z.object({
    labels: z.string().array(),
    datasets: z.object({
      label: z.string(),
      data: z.number().array(),
      borderColor: z.string().optional(),
      backgroundColor: z.string().optional()
    }).array()
  }),
  execute: async function (parameters) {
    return parameters;
  },
});
