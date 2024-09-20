// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse"
import { Button, Space } from "antd"

interface ReportOutputProps {
  reportContent: object
  workflowId: string
}

const ReportOutput: React.FC<ReportOutputProps> = ({ reportContent, workflowId }) => {

  const createReport = () => {
    api.post('/report', {
      name: 'Untitled',
      content: JSON.stringify(reportContent),
      workflow: workflowId
    }).then(({ data }) => {
      const docId = data['id']
      window.open(`/report/${workflowId}/${docId}`, '_ blank')
    })
  }

  return <Space direction="vertical" style={{ width: '100%' }}>
    <Button onClick={createReport} style={{ width: '100%' }}>Create Report</Button>
  </Space>
}

export default ReportOutput
