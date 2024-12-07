"use client"

import { SendOutlined } from "@ant-design/icons"
import { ChatRequestOptions } from "ai"
import { Button, Spin } from "antd"
import React, { useState } from "react"

interface SendButtonProps {
  value: string
  onSubmit: (event?: {
    preventDefault?: () => void;
  }, chatRequestOptions?: ChatRequestOptions) => void
  loading: boolean
}

const SendButton: React.FC<SendButtonProps> = ({ value, onSubmit, loading }) => {

  const size = value === '' && !loading ? 0 : 54

  const handleSubmit = async () => {
    await onSubmit()
  }

  return <Button
    type='primary'
    shape='circle'
    onClick={handleSubmit}
    disabled={loading}
    icon={loading ? <Spin /> : <SendOutlined style={{ fontSize: size === 0 ? 0 : `18px` }} />}
    style={{ width: size, height: size, marginLeft: size === 0 ? 0 : 8, minWidth: 0, padding: size === 0 ? 0 : '4px 0', border: size === 0 ? 0 : 1 }}
  />
}

export default SendButton
