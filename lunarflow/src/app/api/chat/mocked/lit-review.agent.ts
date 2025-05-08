import { ComponentDataType } from "@/models/component/ComponentModel";
import { LunarAgent, ReasoningType } from "../types";

export const litReviewAgent: LunarAgent = {
  instruction: "Based on the set of curated references for Cytokine Release Syndrome (CRS), build a table (Study x Cytokine), which maps each relevant cytokine for CRS and their associated study.",
  agentName: "CRS Literature Review Agent",
  agentDescription: "An agent that processes curated literature on Cytokine Release Syndrome (CRS), extracts cytokine-study associations, and builds a Study x Cytokine table, leveraging advanced reasoning and vocabulary augmentation.",
  inputs: [
    {
      name: "Data Sources Table",
      dataType: ComponentDataType.FILE,
    }
  ],
  reasoningChain: [
    {
      id: "1",
      reasoningType: ReasoningType.DecomposingProblem,
      reasoningDescription: "Selecting supporting agents for the workflow.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Selecting supporting agents to facilitate the literature review and table construction workflow.",
      },
    },
    {
      id: "2",
      reasoningType: ReasoningType.DecomposingProblem,
      reasoningDescription: "Decomposing the reasoning problem into manageable steps.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Breaking down the CRS literature review into granular reasoning tasks for systematic processing.",
      },
    },
    {
      id: "3",
      reasoningType: ReasoningType.GettingTrustedSources,
      reasoningDescription: "Getting cytokine references from the knowledge base (KB). Listing the set of curated relevant references.",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Extracting and listing 17 curated references relevant to CRS from the KB.",
      },
    },
    {
      id: "4",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Parsing documents and separating individual sections, tables, and references.",
      executionTime: 5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Reading each reference, parsing sections (abstract, tables, references) for downstream analysis.",
      },
    },
    {
      id: "5",
      reasoningType: ReasoningType.ExtractingCriteria,
      reasoningDescription: "Organizing citations and extracting metadata (title, authors, journal, year).",
      executionTime: 1,
      output: {
        type: ComponentDataType.TEXT,
        content: "Extracting citation metadata from each reference for accurate study mapping.",
      },
    },
    {
      id: "6",
      reasoningType: ReasoningType.GettingRelevantFacts,
      reasoningDescription: "Getting relevant sections (abstract, discussion, conclusion) directly related to the research question.",
      executionTime: 2,
      output: {
        type: ComponentDataType.TEXT,
        content: "Focusing on and extracting the most relevant sections from each reference to answer the CRS-cytokine association question.",
      },
    },
    {
      id: "7",
      reasoningType: ReasoningType.DecomposingProblem,
      reasoningDescription: "Framing the research question and building a prompt with the research question and relevant literature text.",
      executionTime: 0.5,
      output: {
        type: ComponentDataType.TEXT,
        content: "Formulating the research question: 'Which cytokines are most associated with CRS?' and building a prompt for LLM-based answering.",
      },
    },
    {
      id: "8",
      reasoningType: ReasoningType.ExpandingData,
      reasoningDescription: "Augmenting vocabulary using specialized thesauri (e.g., NCI thesaurus) to enrich cytokine names with synonyms.",
      executionTime: 10,
      output: {
        type: ComponentDataType.TEXT,
        content: "Enriching cytokine names with synonyms and canonical names using the NCI thesaurus; producing a synonym-to-canonical map.",
      },
    },
    {
      id: "9",
      reasoningType: ReasoningType.GeneratingAnalysis,
      reasoningDescription: "Answering the research question based on textual content using LLMs.",
      executionTime: 10,
      output: {
        type: ComponentDataType.TEXT,
        content: "Using LLMs (e.g., GPT-4o) to answer the research question based on the enriched vocabulary and extracted text sections.",
      },
    },
    {
      id: "10",
      reasoningType: ReasoningType.StructuringData,
      reasoningDescription: "Reorganizing table content into factual statements for LLM analysis.",
      executionTime: 10,
      output: {
        type: ComponentDataType.TEXT,
        content: "Transforming literature tables into factual statements for improved LLM analysis.",
      },
    },
    {
      id: "11",
      reasoningType: ReasoningType.GeneratingAnalysis,
      reasoningDescription: "Answering the research question based on table content and extracted facts.",
      executionTime: 10,
      output: {
        type: ComponentDataType.TEXT,
        content: "Using LLMs to answer the research question by analyzing the transformed table facts and enriched vocabulary.",
      },
    },
    {
      id: "12",
      reasoningType: ReasoningType.BuildingTable,
      reasoningDescription: "Building the final Study x Cytokine table associating each cytokine with its relevant study.",
      executionTime: 5,
      output: {
        type: ComponentDataType.CSV,
        content: `Paper,Recombinant Granulocyte-Macrophage Colony-Stimulating Factor,Interleukin-10,Interleukin-1,IL10 wt Allele,Interleukin-2,C-C Motif Chemokine 2,CRP Gene,CRP wt Allele,CCL2 Gene,C-Reactive Protein,CCL2 wt Allele,Interleukin-6,Granulocyte-Macrophage Colony-Stimulating Factor\n"Hong et al., 2021",,X,,X,,,,,,,,X,\n"Sang et al., 2020",,,,,,,X,X,,X,,X,\n"Topp et al., 2021",,,,,X,,X,X,,X,,X,\n"Jacobson et al., 2022",,,,,,,,,,,,X,\n"Hu et al., 2017",,,,,,,X,X,,X,,X,\n"Liu et al., 2021",,,,,,,X,X,,X,,X,\n"Hay et al., 2017",,X,,X,,X,X,X,X,X,X,X,\n"Turtle et al., 2017",,,,,,,X,X,,X,,X,\n"Davila et al., 2014",X,,,,,,X,X,,X,,X,X\n"Porter et al., 2015",X,,,,X,,X,X,,X,,X,X\n"Zhao et al., 2018",,X,X,X,,,X,X,,X,,X,\n"Yan et al., 2019",,,,,,,,,,,,,\n"Neelapu et al., 2017",,,,,,,,,,,,,\n"Yan et al., 2021",,,,,,,,,,,,,\n"Shah et al., 2021",,,,,,,,,,,,,\n"Kalos et al., 2011",,,,,,,,,,,,,`,
      },
    }
  ],
  manualTime: 172800, // 48 hours in seconds
};
