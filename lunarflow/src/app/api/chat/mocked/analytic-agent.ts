import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const analyticAgent: LunarAgent = {
  instruction: "Perform analysis on school construction trends and generate insights",
  agentName: "Analytic Agent",
  agentDescription: "Specialized in analyzing school construction patterns, funding allocation, and regional infrastructure development using demographic, economic, and governmental data.",
  inputs: [
    // {
    //   name: "analysis_query",
    //   dataType: "TEXT",
    // }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningTypeIcon: ReasoningType.DecomposingProblem,
      reasoningType: "Selecting supporting agents",
      reasoningDescription: "Selecting agents to support the workflow.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Selecting supporting agents for the workflow.",
      },
    },
    {
      id: "2",
      reasoningTypeIcon: ReasoningType.ExtractingCriteria,
      reasoningType: "Reasoning about the prompt",
      reasoningDescription: "Interpreting the user's request",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "The analysis will focus on school construction indicators",
      },
    },
    {
      id: "3",
      reasoningTypeIcon: ReasoningType.InterpretingWebSources,
      reasoningType: "Data Fetching",
      reasoningDescription: "Fetch relevant data based on the prompt.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Fetching for data on indicators related to school construction.",
      },
    },
    {
      id: "4",
      reasoningTypeIcon: ReasoningType.ExtractingCriteria,
      reasoningType: "Tools Selection",
      reasoningDescription: "Decide which tools to use (e.g. graph, table).",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Selected visualization tools",
      },
    },
    {
      id: "5",
      reasoningTypeIcon: ReasoningType.GeneratingAnalysis,
      reasoningType: "Response Generation",
      reasoningDescription: "Generate the output.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "The construction of schools in Brazil depends mainly on the growth of the child population, budget availability (minimum of R$ 1,500/student/year) and management efficiency, with large regional disparities - while the Southeast maintains adequate investments, the North faces costs three times higher and lack of access in remote areas. It is also necessary to observe variables such as the number of educational institutions, number of students, HDI (Human Development Index) and education spending. I will present the relevant data in a visual format.",
      },
    },
    {
      id: "6",
      reasoningTypeIcon: ReasoningType.BuildingTable,
      reasoningType: "Selecting ShowTable tool",
      reasoningDescription: "",
      executionTime: 5,
      output: {
        type: ComponentDataType.CSV,
        content: "Region,Municipalities with deficit>30%,Average investment per student (R$),Average school construction cost (R$ million),Average distance to school (km), New schools (2023)\nNorth,68%,1250,4.2,18.5,42\nNortheast,72%,1350,3.8,12.3,87\nCentral-West,45%,1600,3.1,8.7,65\nSoutheast,28%,2200,2.9,5.2,210\nSouth,31%,1950,2.7,4.8,98",
      },
    },
    {
      id: "7",
      reasoningTypeIcon: ReasoningType.GeneratingDataVisualization,
      reasoningType: "Selecting BarChart tool",
      reasoningDescription: "Human Development Index (HDI) per Region",
      executionTime: 5,
      output: {
        type: ComponentDataType.BAR_CHART,
        content: {
          data: {
            "Norte": 0.71,
            "Nordeste": 0.69,
            "Centro-Oeste": 0.76,
            "Sudeste": 0.79,
            "Sul": 0.80
          },
        },
      },
    },
    {
      id: "8",
      reasoningTypeIcon: ReasoningType.GeneratingDataVisualization,
      reasoningType: "Selecting LineChart tool",
      reasoningDescription: "National ",
      executionTime: 5,
      output: {
        type: ComponentDataType.LINE_CHART,
        content: {
          data: {
            "2015": 6.12,
            "2016": 6.22,
            "2017": 6.32,
            "2018": 6.42,
            "2019": 6.5,
            "2020": 6.14,
            "2021": 6.04,
            "2022": 6.16,
            "2023": 6.28
          },
        },
      },
    },
  ],
  manualTime: 30000, // in seconds
}