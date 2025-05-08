import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const wikipediaAgent: LunarAgent = {
  instruction: "Say something interesting about Tigers",
  agentName: "Wikipedia Agent",
  agentDescription: "An agent that searches Wikipedia for information.",
  inputs: [
    // {
    //   name: "Query Input",
    //   dataType: ComponentDataType.TEXT,
    // }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningTypeIcon: ReasoningType.InterpretingWebSources,
      reasoningType: ReasoningType.InterpretingWebSources,
      reasoningDescription: "Searching Wikipedia...",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Tigers are big cats that are native to Asia. They are the largest species of the Felidae family and are known for their distinctive orange coat with black stripes. Tigers are solitary hunters and primarily prey on large ungulates such as deer and wild boar. They are also known for their strength and agility, making them one of the top predators in their habitat.",
      },
    },
    {
      id: "3",
      reasoningTypeIcon: ReasoningType.GettingRelevantFacts,
      reasoningType: ReasoningType.GettingRelevantFacts,
      reasoningDescription: "Summarizing Wikipedia result...",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Tigers are big cats that are native to Asia. They are the largest species of the Felidae family and are known for their distinctive orange coat with black stripes. Tigers are solitary hunters and primarily prey on large ungulates such as deer and wild boar. They are also known for their strength and agility, making them one of the top predators in their habitat.",
      },
    }
  ],
  manualTime: 300, // in seconds
}