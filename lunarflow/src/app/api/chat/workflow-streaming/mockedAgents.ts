import { LunarAgent } from "@/app/api/chat/types";
import { ComponentDataType } from "@/models/component/ComponentModel";

export const wikipediaAgent: LunarAgent = {
  instruction: "Say something interesting about Tigers",
  agentName: "Wikipedia Agent",
  agentDescription: "An agent that searches Wikipedia for information.",
  inputs: [
    {
      name: "Query Input",
      dataType: "TEXT",
    }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningType: "Search",
      reasoningDescription: "Searching Wikipedia...",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Tigers are big cats that are native to Asia. They are the largest species of the Felidae family and are known for their distinctive orange coat with black stripes. Tigers are solitary hunters and primarily prey on large ungulates such as deer and wild boar. They are also known for their strength and agility, making them one of the top predators in their habitat.",
      },
    },
    {
      id: "3",
      reasoningType: "Summarize",
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

export const cytokineCRSAgent: LunarAgent = {
  instruction: "Based on the set of curated references for Cytokine Release Syndrome (CRS), build a table (Study x Cytokine), which maps each relevant cytokine for CRS and their associated study.",
  agentName: "CRS Cytokine Reference Agent",
  agentDescription: "An agent that processes curated references to map cytokines relevant to CRS to their associated studies.",
  inputs: [
    {
      name: "Curated References",
      dataType: "DOCUMENT_SET",
    }
  ],
  reasoningChain: [
    {
      id: "1",
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
      reasoningType: "Decomposing reasoning problem",
      reasoningDescription: "Breaking down the reasoning problem into manageable steps.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Decomposing the reasoning problem for CRS cytokine mapping.",
      },
    },
    {
      id: "3",
      reasoningType: "Getting cytokine references from KB",
      reasoningDescription: "Listing the set of curated relevant references.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "17 references. TODO: List the titles of the paper here.",
      },
    },
    {
      id: "4",
      reasoningType: "Parsing documents",
      reasoningDescription: "Reading the documents and separating individual sections, tables and references.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Documents parsed into sections, tables, and references.",
      },
    },
    {
      id: "5",
      reasoningType: "Organizing citations",
      reasoningDescription: "Extracts metadata necessary for referencing the work (title, authors, journal, publication year).",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Metadata for each reference extracted.",
      },
    },
    {
      id: "6",
      reasoningType: "Getting relevant sections",
      reasoningDescription: "Focusing on the sections which are directly related to the research question (abstract, discussion, conclusion).",
      executionTime: 2,
      output: {
        type: ComponentDataType.TEXT,
        content: "Relevant sections identified: abstract, discussion, conclusion.",
      },
    },
    {
      id: "7",
      reasoningType: "Framing the research question",
      reasoningDescription: "Building a prompt which provides a research question and the relevant literature text from which it could be answered.",
      executionTime: 0.5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Prompt framed: Which cytokines are most associated with CRS?",
      },
    },
    {
      id: "8",
      reasoningType: "Augmenting vocabulary using specialized thesauri",
      reasoningDescription: "Enriching all cytokine names with their synonymous expressions using the NCI thesaurus.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Cytokine names enriched with synonyms and canonical names from the NCI thesaurus.",
      },
    },
    {
      id: "9",
      reasoningType: "Answering the question based on textual content",
      reasoningDescription: "Using an LLM to answer the research question based on the enriched vocabulary and relevant sections.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "LLM-generated answer based on textual content.",
      },
    },
    {
      id: "10",
      reasoningType: "Reorganizing table content",
      reasoningDescription: "Transforming the data presented in tables into factual statements for LLM analysis.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Table data transformed into factual statements.",
      },
    },
    {
      id: "11",
      reasoningType: "Answering the question based on table content",
      reasoningDescription: "Using the LLM to answer the research question based on table-derived facts.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "LLM-generated answer based on table content.",
      },
    },
    {
      id: "12",
      reasoningType: "Building final table",
      reasoningDescription: "Building a table (Study x Cytokine) associating each cytokine relevant to CRS and the associated study.",
      executionTime: 5,
      output: {
        type: ComponentDataType.CSV,
        content: "Study,Cytokine\n[Study 1](https://example.com/study1),Cytokine A\n[Study 2](https://example.com/study2),Cytokine B\n[Study 3](https://example.com/study3),Cytokine C\n[Study 4](https://example.com/study4),Cytokine D\n[Study 5](https://example.com/study5),Cytokine E\n[Study 6](https://example.com/study6),Cytokine F\n[Study 7](https://example.com/study7),Cytokine G\n[Study 8](https://example.com/study8),Cytokine H",
      },
    }
  ],
  manualTime: 172800, // in seconds (48 hours)
}

export const normalizedDbAgent: LunarAgent = {
  instruction: "Describe how to incorporate the listed Brazilian public data sources into a normalized database schema.",
  agentName: "Normalized DB Schema Agent",
  agentDescription: "An agent that analyzes multiple public data sources and executes the queries to create their integration into a normalized relational database.",
  inputs: [
    {
      name: "Data Sources Table",
      dataType: "TABLE",
    }
  ],
  reasoningChain: [
    {
      id: "1",
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
      reasoningType: "Decomposing reasoning problem",
      reasoningDescription: "Breaking down the reasoning problem into manageable steps.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Decomposing the reasoning problem for ETL process.",
      },
    },
    {
      id: "3",
      reasoningType: "Fetch",
      reasoningDescription: "Fetching data from APIs and downloading files as per each data source's specification.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `For each data source, determining the access method (API, file download, or RPA). Using HTTP requests for APIs (e.g., IBGE SIDRA, SICONFI), and download CSV/XLSX/ZIP files for others (e.g., INEP, Atlas Brasil).`
      },
    },
    {
      id: "4",
      reasoningType: "Extract & Parse",
      reasoningDescription: "Parsing and extracting relevant data from each source.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Parsing JSON responses from APIs and extracting relevant fields. For file downloads, extracting and parsing CSV/XLSX/ZIP contents, handling encoding and structure differences. For each dataset, identifying columns for municipality, year, indicator, and value.`
      },
    },
    {
      id: "5",
      reasoningType: "Analyze",
      reasoningDescription: "Analyzing the list of data sources, their update frequency, and data types.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `The data sources include demographic, economic, educational, and fiscal datasets from IBGE, INEP, Tesouro Nacional, and other government portals. They vary in granularity (municipal, state, national) and update frequency (annual, monthly, bimestral).`
      },
    },
    {
      id: "6",
      reasoningType: "Identify Entities",
      reasoningDescription: "Identifying core entities and relationships for normalization.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `Core entities include: Municipality, State, Year/Period, Population, Households, Education Indicators (IDEB, enrollments), Economic Indicators (PIB, transfers), Fiscal Indicators (revenues, expenses, CAPAG, CAUC), and Programs/Proposals (SICONV). Relationships are typically many-to-one (e.g., many indicators per municipality per year).`
      },
    },
    {
      id: "7",
      reasoningType: "Schema Mapping",
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
      reasoningType: "Normalization",
      reasoningDescription: "Ensuring normalization and avoiding redundancy.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: `The schema separates entities (e.g., Municipality, Indicator, Program) and uses foreign keys to link related data. Repeated attributes (e.g., indicator types, sources) are factored into lookup tables. Time-series data is stored in fact tables with references to dimension tables (municipality, year, indicator type).`
      },
    },
    {
      id: "9",
      reasoningType: "Execution",
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