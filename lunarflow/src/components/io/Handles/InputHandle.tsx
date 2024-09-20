// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React from "react"
import Handle from "./Handle"
import { Position } from "reactflow"

interface InputProps extends React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
  id?: string
}

const InputHandle: React.FC<InputProps> = ({ id, ...rest }) => {
  return <div style={{ ...rest.style }} {...rest}>
    <Handle type="target" position={Position.Left} id={id ?? '2'} style={{ marginLeft: -25 }} isConnectableStart={false} />
  </div>
}

export default InputHandle
