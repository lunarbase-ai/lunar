// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ExpandOutlined, ZoomInOutlined, ZoomOutOutlined } from "@ant-design/icons"
import { Button, Space } from "antd"
import { Panel, useReactFlow, useViewport } from "reactflow"

const WorkflowControls: React.FC = () => {

  const { setViewport } = useReactFlow()
  const { x, y, zoom } = useViewport()

  const zoomIn = () => setViewport({ x: x, y: y, zoom: zoom >= 0.5 && zoom < 2 ? zoom + 0.25 : zoom })
  const zoomOut = () => setViewport({ x: x, y: y, zoom: zoom > 0.5 && zoom <= 2 ? zoom - 0.25 : zoom })
  const fitView = () => setViewport({ x: 0, y: 0, zoom: 0.5 })


  return (
    <Panel position="bottom-right">
      <Space.Compact>
        <Button onClick={zoomOut} icon={<ZoomOutOutlined />} />
        <Button onClick={zoomIn} icon={<ZoomInOutlined />} />
        <Button onClick={fitView} icon={<ExpandOutlined />} />
      </Space.Compact>
    </Panel>
  )
}

export default WorkflowControls
