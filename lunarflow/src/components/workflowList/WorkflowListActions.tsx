// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { WarningOutlined } from "@ant-design/icons"
import { Button, Spin, Tooltip } from "antd"
import React, { ReactNode } from "react"

interface Props {
  errors?: string[]
  isLoading?: boolean
  items: ReactNode[]
}

const WorkflowListActions: React.FC<Props> = ({ errors, isLoading, items }) => {
  if (isLoading) {
    return <Spin />
  } else if (errors && errors.length > 0) {
    return <>
      <Tooltip placement="top" title={errors.join('\n\n')}>
        <Button type="text" icon={<WarningOutlined style={{ color: '#f81d22' }} />} />
      </Tooltip>
      {items}
    </>
  }
  return <>
    {items}
  </>
}

export default WorkflowListActions
