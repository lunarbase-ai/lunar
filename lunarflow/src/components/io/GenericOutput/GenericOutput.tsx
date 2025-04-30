/* eslint-disable @next/next/no-img-element */
// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later
"use client"
import { ComponentDataType } from "@/models/component/ComponentModel"
import ReportOutput from "../ReportOutput/ReportOutput"
import LineChartOutput from "../ChartOutputs/LineChartOutput"
import BarChartOutput from "../ChartOutputs/BarChartOutput"
import dynamic from "next/dynamic"
import { File } from "@/models/File"
import CSVOutput from "../CsvOutput/CsvOutput"
import SBGNVisualizer from "../ChartOutputs/SBGNVisualizer/SBGNVisualizer"
import CytoscapeVisualizer from "../ChartOutputs/CytoscapeVisualizer/CytoscapeVisualizer"
import { usePathname } from "next/navigation"
import { Workflow } from "@/models/Workflow"
import MarkdownOutput from "../MarkdownOutput/MarkdownOutput"

const DynamicJSONViewer = dynamic(
  () => import('@/components/JSONViewer'),
  { ssr: false }
)

interface Props {
  workflowId: string
  outputDataType: ComponentDataType
  content: any
  saveWorkflowAction?: (workflow: Workflow, userId: string) => Promise<void>
}

const GenericOutput: React.FC<Props> = ({
  outputDataType,
  content,
  workflowId,
  saveWorkflowAction
}) => {
  const pathname = usePathname()

  const renderFileByType = (file: File) => {
    if (file.type === '.csv' && file.preview) {
      return <CSVOutput csvString={file.preview} />
    } else {
      return <DynamicJSONViewer src={file} />
    }
  }
  const renderOutputByType = (componentType: string, raw: any) => {
    const componentTypeUpper = componentType.toUpperCase()
    if (raw == null || raw === ":undef:") {
      return <></>
    } else if (componentTypeUpper.includes('AUDIO')) {
      return <audio controls src={raw} />
    } else if (componentTypeUpper.includes('STREAM')) {
      return <p>STREAM</p>
    } else if (componentTypeUpper.includes('IMAGE')) {
      return <img src={raw} style={{ width: '100%', height: '100%' }} alt="image output" />
    } else if (componentTypeUpper.includes('LINE_CHART')) {
      return <LineChartOutput data={raw} />
    } else if (componentTypeUpper.includes('BAR_CHART')) {
      return <BarChartOutput data={raw} />
    } else if (componentTypeUpper.includes('REPORT')) {
      return <ReportOutput reportContent={raw} workflowId={workflowId} />
    } else if (outputDataType == ComponentDataType.FILE) {
      const fileContent = content as File
      return renderFileByType(fileContent)
    } else if (componentTypeUpper === 'CSV') {
      return <CSVOutput csvString={raw} />
    } else if (componentTypeUpper.includes('BSGN_GRAPH')) {
      return <SBGNVisualizer
        data={raw}
        pathname={pathname}
        saveWorkflowAction={saveWorkflowAction}
      />
    } else if (componentTypeUpper.includes('CYTOSCAPE')) {
      return <CytoscapeVisualizer
        data={raw}
        pathname={pathname}
        saveWorkflowAction={saveWorkflowAction}
      />
    } else if (typeof raw === 'string' || typeof raw === 'number') {
      return <MarkdownOutput content={typeof raw === 'number' ? raw.toString() : raw} />
    } else {
      return <DynamicJSONViewer src={raw} />
    }
  }
  return <div className="nodrag nowheel">{renderOutputByType(outputDataType, content)}</div>
}

export default GenericOutput
