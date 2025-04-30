import { ComponentDataType } from "@/models/component/ComponentModel";

export type LunarAgentInput = {
  name: string;
  dataType: string;
};

export type LunarAgentReasoningComponentOutput = {
  type: ComponentDataType;
  content: any;
}

export type LunarAgentReasoningComponent = {
  id: string;
  reasoningType: ReasoningType;
  reasoningDescription: string;
  executionTime: number; // in seconds
  output: LunarAgentReasoningComponentOutput;
}

export enum ReasoningType {
  DecomposingProblem = 'Decomposing problem',
  PerformingEquationalReasoning = 'Performing equational reasoning',
  ParametrizingModel = 'Parametrizing model',
  GeneratingCode = 'Generating code',
  BuildingReport = 'Building report',
  BuildingTable = 'Building table',
  RunningSimulation = 'Running simulation',
  GeneratingDataVisualization = 'Generating data visualization',
  InterpretingWebSources = 'Interpreting web sources',
  TranslatingQueriesToDBs = 'Translating queries to DBs',
  ExtractingCriteria = 'Extracting criteria',
  MatchingCriteria = 'Matching criteria',
  FormattingReport = 'Formatting report',
  DesigningSimulation = 'Designing simulation',
  GeneratingLyrics = 'Generating lyrics',
  ComposingMusic = 'Composing music',
  GettingTrustedSources = 'Getting trusted sources',
  GettingOmicsAssociations = 'Getting omics associations',
  PerformingGeneEnrichment = 'Performing gene enrichment',
  SearchingPubmed = 'Searching Pubmed',
  GettingRelevantFacts = 'Getting relevant facts',
  EvaluatingEvidenceStrength = 'Evaluating evidence strength',
  FormalizingIntoLogicalForm = 'Formalizing into logical form',
  VerifyingLogicalCorrectness = 'Verifying logical correctness',
  ProvidingProAndConArguments = 'Providing pro and con arguments',
  SearchingClinicalTrials = 'Searching clinical Trials',
  CombiningEvidence = 'Combining evidence',
  GeneratingAnalysis = 'Generating analysis',
  BuildingMechanisticModel = 'Building mechanistic model',
  QueryingIntegratedDatabase = 'Querying integrated database',
  QueryingGraph = 'Querying graph',
  BuildingGraph = 'Building graph',
  GettingPathwayInformation = 'Getting pathway information',
  GettingGeneFunctions = 'Getting gene functions',
  BuildingMindMap = 'Building mind map',
  GeneratingCounterArguments = 'Generating counter-arguments',
  ReasoningOverFacts = 'Reasoning over facts',
  ReasoningComplete = 'Reasoning complete',
  StructuringData = 'Structuring data',
  ExpandingData = 'Expanding data',
}

export type LunarAgent = {
  instruction: string;
  agentName: string;
  agentDescription: string;
  inputs: LunarAgentInput[];
  reasoningChain: LunarAgentReasoningComponent[];
  manualTime: number; // in seconds
};

export type LunarAgentError = {
  message: string
}

export type LunarComponentInvocationEvent = {
  type: 'lunar-component-invocation';
  toolCallId: string;
  reasoningChainComponent: Omit<LunarAgentReasoningComponent, 'output'> & { output: null };
};

export type LunarComponentResultEvent = {
  type: 'lunar-component-result';
  toolCallId: string;
  reasoningChainComponent: LunarAgentReasoningComponent;
};

export type LunarComponentErrorEvent = {
  type: 'lunar-component-error';
  toolCallId: string;
  lunarAgentError: LunarAgentError;
};

export type LunarAgentResultEvent = {
  type: 'lunar-agent-result';
  toolCallId: string;
  runningTime: number;
  manualtime: number;
};

export type LunarAgentEvent =
  | LunarComponentInvocationEvent
  | LunarComponentResultEvent
  | LunarComponentErrorEvent
  | LunarAgentResultEvent;


