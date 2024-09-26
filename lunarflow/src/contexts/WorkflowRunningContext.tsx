// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { WorkflowRunningType } from "@/models/workflowEditor/WorkflowRunningContext";
import React, { ReactNode, useState } from "react";

export const WorkflowRunningContext = React.createContext<WorkflowRunningType | null>(null)

interface WorkflowRunningProviderProps {
  children: ReactNode
}

const WorkflowRunningProvider: React.FC<WorkflowRunningProviderProps> = ({ children }) => {
  const [isWorkflowRunning, setIsWorkflowRunning] = useState<boolean>(false)

  return <WorkflowRunningContext.Provider value={{ isWorkflowRunning, setIsWorkflowRunning }}>
    {children}
  </WorkflowRunningContext.Provider>
}

export default WorkflowRunningProvider