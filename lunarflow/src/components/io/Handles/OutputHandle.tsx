// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Typography } from "antd"
import React from "react"
import Handle from "./Handle"
import { Position } from "reactflow"

interface OutputHandleProps {
  name: string
}

const OutputHandle: React.FC<OutputHandleProps> = ({ name }) => {
  return <div style={{ position: "relative" }}>
    <Typography style={{ textAlign: "right" }}>{name}</Typography>
    <Handle type="source" position={Position.Right} id={'1'} style={{ marginRight: -25 }} isConnectableEnd={false} />
  </div>
}

export default OutputHandle
