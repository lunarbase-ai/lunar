// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { Input } from "antd"
import { useContext } from "react"

const HeaderInput = () => {
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  return <Input
    value={workflowEditor.name}
    onChange={(event) => setValues(event.target.value)}
    style={{
      maxWidth: 280,
      textAlign: 'center',
      color: '#fff',
      position: 'absolute',
      right: 0,
      left: 0,
      marginLeft: 'auto',
      marginRight: 'auto',
    }}
    bordered={false}
  />
}

export default HeaderInput
