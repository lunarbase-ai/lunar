import { tool as createTool } from 'ai';
import { z } from 'zod';

export const barChart = createTool({
  description: "Display the bar chart for a list of labels and an array of numbers data. When you call it, it already renders, so you don't need to reference it later",
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

export const tools = {
  barChart: barChart,
};
