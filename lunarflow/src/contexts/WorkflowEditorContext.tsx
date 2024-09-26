// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from '@/models/component/ComponentModel';
import { WorkflowEditor } from '@/models/workflowEditor/WorkflowEditor';
import { WorkflowEditorContextType } from '@/models/workflowEditor/WorkflowEditorContextType';
import React, { ReactNode, useState } from 'react';

export const WorkflowEditorContext = React.createContext<WorkflowEditorContextType | null>(null);

interface WorkflowEditorProviderProps {
  children: ReactNode
  initialComponents: ComponentModel[]
}

const WorkflowEditorProvider: React.FC<WorkflowEditorProviderProps> = ({ children, initialComponents }) => {
  const [workflowEditor, setWorkflowEditor] = React.useState<WorkflowEditor>({
    name: '',
    description: '',
    errors: [],
    results: {},
  })
  const [components, setComponents] = useState<ComponentModel[]>(initialComponents)
  const setValues = (name?: string, description?: string, errors?: string[], results?: Record<string, ComponentModel>) => {
    const newEditor = { ...workflowEditor }
    newEditor.name = name ?? newEditor.name
    newEditor.description = description ?? newEditor.description
    newEditor.errors = errors ?? newEditor.errors ?? []
    newEditor.results = results ?? newEditor.results
    setWorkflowEditor(newEditor)
  }

  return <WorkflowEditorContext.Provider value={{ workflowEditor, setValues, components, setComponents }}>
    {children}
  </WorkflowEditorContext.Provider>
}

export default WorkflowEditorProvider
