"use server"

import api from "../api/lunarverse"
import { Report } from '@/models/Report';

export const createReportAction = async (reportName: string, reportContent: string, workflowId: string, userId: string) => {
  const { data } = await api.post(`/report?user_id=${userId}`, {
    name: reportName,
    content: JSON.stringify(reportContent),
    workflow: workflowId
  })
  return data
}

export const getReportAction = async (workflowId: string, reportId: string, userId: string) => {
  const { data } = await api.get<Report>(`/report/${workflowId}/${reportId}?user_id=${userId}`)
  return data
}