// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "@/models/component/ComponentModel"
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons"
import { Button, Input, List, Modal, Row, Space, TreeDataNode } from "antd"
import Tree, { DataNode } from "antd/es/tree"
import { useEffect, useState } from "react"
import { useEdges, useNodes, Node } from "reactflow"

const { Item } = List

interface PropertySelectorProps {
  value: string
  nodeId: string
  onInputChange: (value: any) => void
}

const PropertySelector: React.FC<PropertySelectorProps> = ({
  value,
  nodeId,
  onInputChange,
}) => {
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  const [selectedKeys, setSelectedKeys] = useState<string[]>()
  const [newSelectedKey, setNewSelectedKey] = useState<string>('')
  const edges = useEdges()
  const nodes = useNodes<ComponentModel>()

  useEffect(() => {
    if (!value || value === ":undef:" || value === '') {
      setSelectedKeys(undefined)
    } else {
      setSelectedKeys(value.split(','))
    }
  }, [value])

  const handleOk = () => {
    onInputChange(selectedKeys?.join(',') ?? undefined)
    setIsModalOpen(false)
    setLoading(false)
  };

  const handleCancel = () => {
    setIsModalOpen(false)
    setLoading(false)
  }

  const buildProperties = (io: any, nodeId: string, path: string = '') => {
    if (io && !Array.isArray(io) && typeof io === 'object') {
      const properties: DataNode[] = []
      Object.keys(io).forEach(propertyString => {
        const key = path === '' ? propertyString : `${path}.${propertyString}`
        const property: TreeDataNode = {
          key: key,
          title: propertyString,
          children: buildProperties(io[propertyString], nodeId, key),
          checkable: true
        }
        properties.push(property)
      })
      return properties
    }
    return []
  }

  const getProperties = () => {
    const inputNodeIds = edges.filter(edge => edge.target === nodeId).map(edge => edge.source) ?? []
    const inputNodes: Node<ComponentModel>[] = nodes.filter(node => inputNodeIds.includes(node.id))
    return inputNodes.map(node => {
      const component: TreeDataNode = {
        key: node.id,
        title: node.id,
        children: buildProperties(node.data.output.value, nodeId),
        checkable: false
      }
      return component
    })
  }

  const unselectKey = (key: string) => {
    if (Array.isArray(selectedKeys)) setSelectedKeys([...selectedKeys].filter(element => element !== key))
  }

  const addSelectedKey = (key: string) => {
    if (!Array.isArray(selectedKeys)) return
    if (!selectedKeys.includes(key)) {
      setSelectedKeys(selectedKeys ? [...selectedKeys, key] : [key])
    }
  }

  return <>
    <Button style={{ width: '100%' }} onClick={() => setIsModalOpen(true)}>Select Properties</Button>
    <Modal
      title="Property selector"
      open={isModalOpen}
      onOk={handleOk}
      onCancel={handleCancel}
      width={720}
      footer={[
        <Button key="back" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleOk}>
          Ok
        </Button>
      ]}
    >
      <Row>
        <Tree
          checkStrictly
          checkable
          checkedKeys={selectedKeys}
          defaultSelectedKeys={['0-1']}
          treeData={getProperties()}
          onCheck={(checked) => Array.isArray(checked)
            ? setSelectedKeys(checked as string[])
            : setSelectedKeys(checked.checked as string[])}
          blockNode
          rootStyle={{ flexGrow: 1, paddingRight: 8, maxWidth: '50%', overflowX: 'scroll' }}
        />
        <List
          header={
            <Space.Compact style={{ width: '100%' }}>
              <Input value={newSelectedKey} onChange={(event => setNewSelectedKey(event.target.value))} placeholder="Add a new property to select..." />
              <Button onClick={() => addSelectedKey(newSelectedKey)} icon={<PlusOutlined />} />
            </Space.Compact>
          }
          dataSource={selectedKeys}
          renderItem={(item) => <Item actions={[<Button key={'remove'} icon={<DeleteOutlined />} onClick={() => unselectKey(item)} />]}>{item}</Item>}
          style={{ width: '50%', overflow: 'hidden' }}
        />
      </Row>
    </Modal>
  </>
}

export default PropertySelector
