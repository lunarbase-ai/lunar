// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Button, Card, List, Modal, Spin, Typography, message } from "antd"
import { DeleteOutlined, ExclamationCircleFilled } from "@ant-design/icons"
import { useState } from "react"
import { ComponentModel } from "@/models/component/ComponentModel"
import { useRouter } from "next/navigation"
import './styles.css'
import { useUserId } from "@/hooks/useUserId"
import { createWorkflowFromComponentExample } from "@/app/actions/workflows"
import { deleteComponentAction } from "@/app/actions/components"
import { SessionProvider } from "next-auth/react"

const { confirm } = Modal
const { Link } = Typography

interface ComponentListProps {
  components: ComponentModel[]
}

const ComponentList: React.FC<ComponentListProps> = (props) => {
  return <SessionProvider>
    <ComponentListContent {...props} />
  </SessionProvider>
}

const ComponentListContent: React.FC<ComponentListProps> = ({ components }) => {
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({})
  const [messageApi, contextHolder] = message.useMessage()
  const router = useRouter()
  const userId = useUserId()

  //TODO: Handle loading
  if (!userId) return <></>

  const showConfirm = (componentId: string) => {
    confirm({
      title: 'Do you really want to delete this component?',
      icon: <ExclamationCircleFilled />,
      onOk() {
        removeComponent(componentId)
      },
      onCancel() {
      },
    })
  }

  const removeComponent = (componentId: string) => {
    messageApi.destroy()
    setIsLoading(prevLoading => ({ ...prevLoading, [componentId]: true }))
    deleteComponentAction(componentId, userId)
      .then(() => {
        messageApi.success('The component has been deleted successfully')
        router.refresh()
      })
      .catch((error) => {
        messageApi.error({
          content: error.message ?? `Failed to delete component. Details: ${error}`,
          onClick: () => messageApi.destroy()
        }, 0)
      })
      .finally(() => {
        setIsLoading(prevLoading => ({ ...prevLoading, [componentId]: false }))
      })
  }

  const renderDeleteButton = (component: ComponentModel) => {
    const componentId = component.id
    if (componentId == null) { return <></> }
    if (isLoading[componentId]) { return <Spin /> }
    if (component.isCustom) return <Button
      onClick={() => showConfirm(componentId)}
      type="text"
      icon={<DeleteOutlined />}
      loading={isLoading[componentId]}
    />
    return <></>
  }

  const customComponents = components.filter(component => component.isCustom)

  return <>
    {contextHolder}
    {customComponents.length > 0 ? <List
      grid={{ gutter: 16, column: 2 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{
          fontSize: 24,
          fontWeight: 'bold',
          color: '#0D181C',
          marginBottom: 16,
        }}>
          Custom Components
        </h2>
        <Button onClick={() => router.push('/component')}>
          Create new component
        </Button>
      </div>}
      itemLayout="horizontal"
      dataSource={customComponents}
      renderItem={(component) => {
        const componentId = component.id
        if (componentId == null) return <></>
        return <>
          <List.Item key={componentId}>
            <Card
              title={<Link onClick={() => router.push(`/component/${componentId}`)}>{component.name}</Link>}
              extra={renderDeleteButton(component)}
            >
              {component.description}
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    /> : <></>}
    <List
      grid={{ gutter: 16, column: 3 }}
      header={<div style={{ display: 'flex', justifyContent: 'space-between' }}>
        {customComponents.length > 0 ? <h2 style={{
          fontSize: 24,
          fontWeight: 'bold',
          color: '#0D181C',
          marginBottom: 16,
        }}>
          Core Components
        </h2> : <>
          <h2 style={{
            fontSize: 24,
            fontWeight: 'bold',
            color: '#0D181C',
            marginBottom: 16,
          }}>
            Component Library
          </h2>
          <Button onClick={() => router.push('/component')}>
            Create new component
          </Button>
        </>}
      </div>}
      itemLayout="horizontal"
      dataSource={components.filter(component => !component.isCustom)}
      renderItem={(component) => {
        const componentId = component.id
        const componentLabel = component.label
        if (componentId == null || componentLabel == null) return <></>
        return <>
          <List.Item key={componentId}>
            <Card
              title={component.name}
              extra={component.componentExamplePath !== null ? <Button
                type="link"
                onClick={async () => {
                  setIsLoading(prevLoading => ({ ...prevLoading, [componentId]: true }))
                  try {
                    const result = await createWorkflowFromComponentExample(componentId, userId)
                    router.push(`/editor/${result.id}`)
                  } catch (e) {
                    console.error(e)
                  }
                  setIsLoading(prevLoading => ({ ...prevLoading, [componentId]: false }))
                }}
                loading={isLoading[componentId]}>Try it out</Button> : <></>}
              style={{
                height: 255,
                display: 'flex',
                flexDirection: 'column',
              }}
              styles={{
                body: {
                  overflow: 'hidden',
                }
              }}
            >
              <p style={{
                height: '100%',
                overflow: 'hidden',
              }}>
                {component.description}
              </p>
            </Card>
          </List.Item>
        </>
      }}
      style={{
        marginTop: 16
      }}
    />
  </>
}

export default ComponentList