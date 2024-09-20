// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React from "react"
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { getParameters } from "@/utils/helpers";

interface CodeEditorProps {
  value: string
  mode: string
  onChange?: ((value: string, event?: any) => void)
  onParametersChange?: (parameters: string[]) => void
}

const CodeEditor: React.FC<CodeEditorProps> = ({ onChange, onParametersChange, value, mode }) => {

  const handleChange = (value: string, event?: any) => {
    if (onChange != null) onChange(value)
    if (onParametersChange != null) onParametersChange(getParameters(value))
  }

  return <CodeMirror
    extensions={[python()]}
    style={{
      backgroundColor: "#f5f5f5",
      height: "100%",
      minHeight: 300,
      fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
    }}
    width="100%"
    onChange={handleChange}
    value={value}
  />
}

export default CodeEditor