// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { ChatRequestOptions } from "ai"
import { Spin } from "antd"
import React from "react"
import Button from "./Button"
import { LoadingOutlined, SendOutlined } from "@ant-design/icons"

interface SendButtonProps {
  value: string
  onSubmit: (event?: {
    preventDefault?: () => void;
  }, chatRequestOptions?: ChatRequestOptions) => void
  loading: boolean
}

const SendButton: React.FC<SendButtonProps> = ({ value, onSubmit, loading }) => {

  const size = value === '' && !loading ? 0 : 54

  return <Button
    type='primary'
    onClick={onSubmit}
    disabled={loading || value === ''}
    icon={loading
      ? <LoadingOutlined />
      : <SendOutlined style={{ fontSize: `18px` }} />
    }
    iconPosition="end"
  >
    Send
  </Button>
}

export default SendButton
