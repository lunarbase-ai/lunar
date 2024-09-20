// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import React from 'react'
import Password from 'antd/es/input/Password'

interface Props {
  value: string
  onChange: (value: string) => void
}

const PasswordInput: React.FC<Props> = ({
  value,
  onChange,
}) => {
  return <div style={{ fontFamily: '"Source Code Pro", monospace', width: '100%', inset: 0, position: 'absolute' }}>
    <Password
      style={{ width: '100%', fontFamily: '"Source Code Pro", monospace', position: 'absolute', zIndex: 1, background: 'transparent' }}
      value={value}
      type='password'
      onChange={(value) => {
        if (onChange != null) onChange(value.target.value)
      }}
      className="nodrag"
    />
  </div>
}

export default PasswordInput
