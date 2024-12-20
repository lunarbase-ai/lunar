// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { useUserId } from "@/hooks/useUserId"
import { ComponentModel } from "@/models/component/ComponentModel"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { Button, Form, Input, Modal, Typography, message } from "antd"
import { useForm } from "antd/es/form/Form"
import { useRouter } from "next/navigation"
import React, { useContext, useEffect, useState } from "react"
import { useNodes } from "reactflow"
import { Node } from "reactflow"
import GenericSettingInput from "./GenericSettingInput"
import { deleteComponentAction, saveComponentAction } from "@/app/actions/components"
import { convertClientToComponentModel } from "@/utils/workflows"

const { Text } = Typography

export interface ConfigurationModalProps {
  id: string
  configuration: Record<string, string>
  open: boolean
  component: ComponentModel
  type: string
  close: () => void
  setNodes: React.Dispatch<React.SetStateAction<Node<ComponentModel, string | undefined>[]>>
}

const ConfigurationModal: React.FC<ConfigurationModalProps> = ({
  id,
  configuration,
  open,
  component,
  type,
  close,
  setNodes
}) => {
  const [form] = useForm()
  const [customComponentForm] = useForm()
  const nodes = useNodes<ComponentModel>()
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()
  const router = useRouter()
  const [isNewComponentModalOpen, setIsNewComponentModalOpen] = useState<boolean>(false)
  const [isDeletionModalOpen, setIsDeletionModalOpen] = useState<boolean>(false)
  const { components, setComponents } = useContext(WorkflowEditorContext) as WorkflowEditorContextType

  useEffect(() => {
    Object.keys(configuration).forEach(key => {
      if (key === 'force_run') {
        form.setFieldValue(key, configuration[key] !== 'false')
      } else {
        form.setFieldValue(key, configuration[key])
      }
    })
  }, [configuration])

  if (!userId) return <></>

  const createCustomComponent = (name: string, description: string) => {
    const newComponent: ComponentModel = {
      ...component,
      name,
      description,
      // className: type,
      group: "CUSTOM",
      isCustom: true,
    }
    saveComponentAction(convertClientToComponentModel(newComponent), userId)
      .then(() => {
        setComponents([...components, newComponent])
        messageApi.open({
          type: 'success',
          content: 'Your custom component has been saved'
        })
      })
      .catch(error => {
        console.error(error)
        messageApi.open({
          type: 'error',
          content: 'Failed to save your custom component'
        })
      })
      .finally(() => setIsNewComponentModalOpen(false))
  }

  const deleteComponent = () => {
    if (component.id) {
      deleteComponentAction(component.id, userId)
        .then(() => {
          const componentsCopy: ComponentModel[] = []
          components.forEach(sidebarComponent => {
            if (sidebarComponent.id !== component.id) {
              componentsCopy.push(sidebarComponent)
            }
          })
          setComponents(componentsCopy)
          messageApi.open({
            type: 'success',
            content: 'Your custom component has been deleted'
          })
          setIsDeletionModalOpen(false)
        })
        .catch(error => {
          console.error(error)
          messageApi.open({
            type: 'error',
            content: 'Failed to delete your custom component'
          })
          setIsDeletionModalOpen(false)
        })
    } else {
      //TODO: Add feedback
    }
  }

  const setConfiguration = () => {
    const newConfiguration: Record<string, any> = form.getFieldsValue()
    const formattedNewConfiguration: Record<string, string> = {}
    Object.keys(newConfiguration).map(key => {
      const config = newConfiguration[key]
      if (config === null) {
        formattedNewConfiguration[key] = config
      } else {
        formattedNewConfiguration[key] = config
      }
    })

    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === id) {
          node.data = {
            ...node.data,
            configuration: formattedNewConfiguration,
          }
        }
        return node;
      })
    )
  }

  const handleFormSubmit = () => {
    setConfiguration()
    close()
  }

  const handleCreateCustomComponent = () => {
    setConfiguration()
    setIsNewComponentModalOpen(true)
  }

  const handleCancel = () => {
    const savedArguments = nodes.find(node => node.id === id)?.data.configuration
    if (savedArguments != null) {
      Object.keys(savedArguments).forEach(key => {
        form.setFieldValue(key, savedArguments[key])
      })
    }
    close()
  }

  const isValidString = (string?: string) => {
    if (string != null) {
      return string.length > 0
    } else {
      return false
    }
  }

  const handleComponentOk = () => {
    const customComponentName = customComponentForm.getFieldValue('name')
    const customComponentDescription = customComponentForm.getFieldValue('description')
    if (isValidString(customComponentName) && isValidString(customComponentDescription)) {
      createCustomComponent(customComponentName, customComponentDescription)
    }
  }

  return <Modal
    title={`${component.name} settings`}
    open={open}
    onCancel={handleCancel}
    onOk={handleFormSubmit}
  >
    {contextHolder}
    <Form form={form} layout="vertical" initialValues={configuration}>
      {Object.keys(configuration).map((setting, key) => {
        return (
          <Form.Item
            label={setting.replaceAll('_', ' ')}
            name={setting}
            key={key}
          >
            <GenericSettingInput settingKey={setting} form={form} />
          </Form.Item>
        )
      })
      }
    </Form>
    <Modal
      title="Create new custom component"
      open={isNewComponentModalOpen}
      onCancel={() => setIsNewComponentModalOpen(false)}
      onOk={handleComponentOk}
    >
      <Form
        form={customComponentForm}
        layout="vertical"
      >
        <Form.Item
          label="Component name"
          name="name"
          rules={[{ required: true, message: 'Please input a name' }]}
        >
          <Input
            onChange={
              (event) => customComponentForm.setFieldValue(
                "name",
                event.target.value
              )
            }
          />
        </Form.Item>
        <Form.Item
          label="Component description"
          name="description"
          rules={[{ required: true, message: 'Please input a description' }]}
        >
          <Input
            onChange={
              (event) => customComponentForm.setFieldValue(
                "description",
                event.target.value
              )
            }
          />
        </Form.Item>
      </Form>
    </Modal>
    <Button
      onClick={handleCreateCustomComponent}
      style={{ width: '100%', marginBottom: 16 }}
    >
      Create custom component
    </Button>
    {component.isCustom && component.componentCode ? <Button
      onClick={() => router.push(`/component/${component.id}`)}
      style={{ width: '100%', marginBottom: 16 }}
    >
      Edit custom component
    </Button> : <></>}
    {component.isCustom ? <Button
      danger
      onClick={() => setIsDeletionModalOpen(true)}
      style={{ width: '100%' }}
    >
      Delete custom component
    </Button> : <></>}
    <Modal open={isDeletionModalOpen} onCancel={() => setIsDeletionModalOpen(false)} onOk={deleteComponent}>
      <Text>Do you really want to delete this component?</Text>
    </Modal>
  </Modal>
}

export default ConfigurationModal
