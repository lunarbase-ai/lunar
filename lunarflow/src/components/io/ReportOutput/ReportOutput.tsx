// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { createReportAction } from "@/app/actions/report"
import { useUserId } from "@/hooks/useUserId"
import { Button, Space } from "antd"

interface ReportOutputProps {
  reportContent: object
  workflowId: string
}

const ReportOutput: React.FC<ReportOutputProps> = ({ reportContent, workflowId }) => {
  const userId = useUserId()

  if (!userId) return <></>

  const createReport = () => {
    createReportAction("Untitled", JSON.stringify(reportContent), workflowId, userId)
      .then((result) => {
        const docId = result['id']
        window.open(`/report/${workflowId}/${docId}`, '_blank')
      })
  }

  return <Space direction="vertical" style={{ width: '100%' }}>
    <Button onClick={createReport} style={{ width: '100%' }}>Create Report</Button>
  </Space>
}

export default ReportOutput
