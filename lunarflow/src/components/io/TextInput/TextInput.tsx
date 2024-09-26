// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import React from 'react'
import { Input } from 'antd'

interface Props {
  value: string
  onChange: (value: string) => void
}

const TextInput: React.FC<Props> = ({
  value,
  onChange,
}) => {
  return <div style={{
    maxHeight: 200,
    overflowY: 'scroll',
    width: '100%',
    fontFamily: 'Source Code Pro, monospace',
    inset: 0,
  }}>
    <Input.TextArea
      value={value}
      onChange={(value) => {
        if (onChange != null) onChange(value.target.value)
      }}
      autoSize
      className="nodrag"
      style={{
        width: '100%',
        fontFamily: 'Source Code Pro, monospace',
        zIndex: 1,
        background: 'transparent',
      }}
    />
  </div >
}

export default TextInput
