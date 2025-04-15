// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"

import { WorkflowReference } from "@/models/Workflow"
import { Button, Checkbox, List, Modal } from "antd"
import { CheckboxChangeEvent } from "antd/es/checkbox/Checkbox"
import { useState } from "react"

interface ChatInputProps {
  workflows: WorkflowReference[]
  selectedWorkflowIds: string[]
  setSelectedWorkflowIds: (workflowIds: string[]) => void
}

const ChatHeader: React.FC<ChatInputProps> = ({ workflows, selectedWorkflowIds, setSelectedWorkflowIds }) => {

  const [isSelectModalOpen, setIsSelectModalOpen] = useState<boolean>(false)

  const handleCheckbox = (event: CheckboxChangeEvent, workflowId: string) => {
    if (event.target.checked) {
      const newWorkflowIds = [...selectedWorkflowIds, workflowId]
      setSelectedWorkflowIds(newWorkflowIds)
    } else {
      const workflowIdsCopy = [...selectedWorkflowIds]
      const index = workflowIdsCopy.indexOf(workflowId)
      workflowIdsCopy.splice(index, 1)
      setSelectedWorkflowIds(workflowIdsCopy)
    }
  }

  return <div style={{
    position: 'sticky',
    zIndex: 10,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 8,
    top: 0,
    right: 0,
    left: 0,
    width: '100%',
    backgroundColor: '#fff'
  }}>
    <Modal
      title="Select the workflows Lunar can execute"
      open={isSelectModalOpen}
      onCancel={() => setIsSelectModalOpen(false)}
      onClose={() => setIsSelectModalOpen(false)}
      onOk={() => setIsSelectModalOpen(false)}
    >
      <List
        dataSource={workflows}
        renderItem={(item, index) => (
          <List.Item key={index}>
            <List.Item.Meta
              title={item.name}
              description={item.description}
            />
            <Checkbox onChange={(event) => handleCheckbox(event, item.id)} />
          </List.Item>
        )}
      />
    </Modal>
    <Button onClick={() => {
      setIsSelectModalOpen(true)
    }}>Select workflows</Button>
  </div>
}

export default ChatHeader
