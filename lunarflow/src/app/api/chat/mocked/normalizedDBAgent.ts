import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const normalizedDbAgent: LunarAgent = {
  instruction: "Incorporate the listed Brazilian public data sources into a normalized database schema.",
  agentName: "Normalized DB Schema Agent",
  agentDescription: "An agent that analyzes multiple public data sources and executes the queries to create their integration into a normalized relational database.",
  inputs: [
    // {
    //   name: "Data Sources Table",
    //   dataType: ComponentDataType.FILE,
    // }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningTypeIcon: ReasoningType.DecomposingProblem,
      reasoningType: ReasoningType.DecomposingProblem,
      reasoningDescription: "Selecting agents to support the workflow.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Selecting supporting agents for the workflow.",
      },
    },
    {
      id: "2",
      reasoningTypeIcon: ReasoningType.DecomposingProblem,
      reasoningType: ReasoningType.DecomposingProblem,
      reasoningDescription: "Breaking down the reasoning problem into manageable steps.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Decomposing the reasoning problem for ETL process.",
      },
    },
    {
      id: "3",
      reasoningTypeIcon: ReasoningType.InterpretingWebSources,
      reasoningType: ReasoningType.InterpretingWebSources,
      reasoningDescription: "Fetching data from APIs and downloading files as per each data source's specification from Data Sources KB.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `For each data source, determining the access method (API, file download, or RPA). Using HTTP requests for APIs (e.g., IBGE SIDRA, SICONFI), and download CSV/XLSX/ZIP files for others (e.g., INEP, Atlas Brasil).`
      },
    },
    {
      id: "4",
      reasoningTypeIcon: ReasoningType.ExtractingCriteria,
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Parsing and extracting relevant data from each source.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Parsing JSON responses from APIs and extracting relevant fields. For file downloads, extracting and parsing CSV/XLSX/ZIP contents, handling encoding and structure differences. For each dataset, identifying columns for municipality, year, indicator, and value.`
      },
    },
    {
      id: "5",
      reasoningTypeIcon: ReasoningType.GeneratingAnalysis,
      reasoningType: ReasoningType.GeneratingAnalysis,
      reasoningDescription: "Analyzing the list of data sources, their update frequency, and data types.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `The data sources include demographic, economic, educational, and fiscal datasets from IBGE, INEP, Tesouro Nacional, and other government portals. They vary in granularity (municipal, state, national) and update frequency (annual, monthly, bimestral).`
      },
    },
    {
      id: "6",
      reasoningTypeIcon: ReasoningType.ExtractingCriteria,
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Identifying core entities and relationships for normalization.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Core entities include: Municipality, State, Year/Period, Population, Households, Education Indicators (IDEB, enrollments), Economic Indicators (PIB, transfers), Fiscal Indicators (revenues, expenses, CAPAG, CAUC), and Programs/Proposals (SICONV). Relationships are typically many-to-one (e.g., many indicators per municipality per year).`
      },
    },
    {
      id: "7",
      reasoningTypeIcon: ReasoningType.StructuringData,
      reasoningType: ReasoningType.StructuringData,
      reasoningDescription: "Mapping data sources to normalized tables and foreign keys.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Each data source maps to one or more tables. For example:
- Municipality (id, name, state_id, IBGE_code, etc.)
- State (id, name, UF)
- Population (municipality_id, year, value, source)
- Education_Indicator (municipality_id, year, type, value, source)
- Economic_Indicator (municipality_id, year, type, value, source)
- Fiscal_Indicator (municipality_id, year, type, value, source)
- SICONV_Proposal (proposal_id, municipality_id, year, details)
All tables use foreign keys to Municipality and Year. Lookup tables (e.g., IndicatorType, Source) ensure normalization.`
      },
    },
    {
      id: "8",
      reasoningTypeIcon: ReasoningType.StructuringData,
      reasoningType: ReasoningType.StructuringData,
      reasoningDescription: "Ensuring normalization and avoiding redundancy.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `The schema separates entities (e.g., Municipality, Indicator, Program) and uses foreign keys to link related data. Repeated attributes (e.g., indicator types, sources) are factored into lookup tables. Time-series data is stored in fact tables with references to dimension tables (municipality, year, indicator type).`
      },
    },
    {
      id: "9",
      reasoningTypeIcon: ReasoningType.GeneratingCode,
      reasoningType: ReasoningType.GeneratingCode,
      reasoningDescription: "Executing the schema creation and data loading.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Using SQL commands to create tables and relationships. For each data source, loading data into the corresponding table, ensuring data integrity and consistency.`
      },
    }
  ],
  manualTime: 172800, // in seconds
}