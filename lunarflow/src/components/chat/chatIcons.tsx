import { ReasoningType } from "@/app/api/chat/types";

import DecomposingProblemSvg from '@/assets/icons/decomposing_problem.svg';
import ParametrizingModelSvg from '@/assets/icons/parametrizing_model.svg';
import GeneratingCodeSvg from '@/assets/icons/generating_code.svg';
import GeneratingCounterArgumentsSvg from '@/assets/icons/generating_counter-arguments.svg';
import EvaluatingEvidenceStrengthSvg from '@/assets/icons/evaluating_evidence_strength.svg';
import VerifyingLogicalCorrectnessSvg from '@/assets/icons/verifying_logical_correctness.svg';
import ReasoningOverFactsSvg from '@/assets/icons/reasoning_over_facts.svg';
import BuildingMechanisticModelSvg from '@/assets/icons/building_mechanistic_model.svg';
import ExtractingCriteriaSvg from '@/assets/icons/extracting_criteria.svg';
import GeneratingDataVisualizationSvg from '@/assets/icons/generating_data_visualization.svg';
import GettingTrustedSourcesSvg from '@/assets/icons/getting_trusted_sources.svg';
import InterpretingWebSources from '@/assets/icons/interpreting_web_sources.svg';
import DefaultIcon from '@/assets/icons/reasoning_over_facts.svg';

export const ReasoningTypeIcons: Record<ReasoningType, any> = {
  [ReasoningType.DecomposingProblem]: DecomposingProblemSvg,
  [ReasoningType.PerformingEquationalReasoning]: DefaultIcon,
  [ReasoningType.ParametrizingModel]: ParametrizingModelSvg,
  [ReasoningType.GeneratingCode]: GeneratingCodeSvg,
  [ReasoningType.BuildingReport]: DefaultIcon,
  [ReasoningType.BuildingTable]: DefaultIcon,
  [ReasoningType.RunningSimulation]: DefaultIcon,
  [ReasoningType.GeneratingDataVisualization]: GeneratingDataVisualizationSvg,
  [ReasoningType.InterpretingWebSources]: InterpretingWebSources,
  [ReasoningType.TranslatingQueriesToDBs]: DefaultIcon,
  [ReasoningType.ExtractingCriteria]: ExtractingCriteriaSvg,
  [ReasoningType.MatchingCriteria]: DefaultIcon,
  [ReasoningType.FormattingReport]: DefaultIcon,
  [ReasoningType.DesigningSimulation]: DefaultIcon,
  [ReasoningType.GeneratingLyrics]: DefaultIcon,
  [ReasoningType.ComposingMusic]: DefaultIcon,
  [ReasoningType.GettingTrustedSources]: GettingTrustedSourcesSvg,
  [ReasoningType.GettingOmicsAssociations]: DefaultIcon,
  [ReasoningType.PerformingGeneEnrichment]: DefaultIcon,
  [ReasoningType.SearchingPubmed]: DefaultIcon,
  [ReasoningType.GettingRelevantFacts]: DefaultIcon,
  [ReasoningType.EvaluatingEvidenceStrength]: EvaluatingEvidenceStrengthSvg,
  [ReasoningType.FormalizingIntoLogicalForm]: DefaultIcon,
  [ReasoningType.VerifyingLogicalCorrectness]: VerifyingLogicalCorrectnessSvg,
  [ReasoningType.ProvidingProAndConArguments]: DefaultIcon,
  [ReasoningType.SearchingClinicalTrials]: DefaultIcon,
  [ReasoningType.CombiningEvidence]: DefaultIcon,
  [ReasoningType.GeneratingAnalysis]: DefaultIcon,
  [ReasoningType.BuildingMechanisticModel]: BuildingMechanisticModelSvg,
  [ReasoningType.QueryingIntegratedDatabase]: DefaultIcon,
  [ReasoningType.QueryingGraph]: DefaultIcon,
  [ReasoningType.BuildingGraph]: DefaultIcon,
  [ReasoningType.GettingPathwayInformation]: DefaultIcon,
  [ReasoningType.GettingGeneFunctions]: DefaultIcon,
  [ReasoningType.BuildingMindMap]: DefaultIcon,
  [ReasoningType.GeneratingCounterArguments]: GeneratingCounterArgumentsSvg,
  [ReasoningType.ReasoningOverFacts]: ReasoningOverFactsSvg,
  [ReasoningType.ReasoningComplete]: DefaultIcon,
  [ReasoningType.StructuringData]: DefaultIcon,
  [ReasoningType.ExpandingData]: DefaultIcon,
};