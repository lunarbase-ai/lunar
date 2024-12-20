// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Divider, Menu, MenuProps } from "antd"
import Sider from "antd/es/layout/Sider"
import React, { useCallback, useContext, useEffect, useState } from "react"
import { ApiOutlined, AppstoreOutlined, BulbOutlined, CodeOutlined, DatabaseOutlined, EllipsisOutlined, FileDoneOutlined, FileSearchOutlined, FormOutlined, GlobalOutlined, InsertRowBelowOutlined, LoginOutlined, MessageOutlined, SearchOutlined } from '@ant-design/icons'
import Input from "antd/es/input/Input"
import _ from "lodash"
import { ComponentModel } from "@/models/component/ComponentModel"
import { useUserId } from "@/hooks/useUserId"
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { WorkflowEditorContextType } from "@/models/workflowEditor/WorkflowEditorContextType"
import { searchComponentsAction } from "@/app/actions/components"

const onDragStart = (event: React.DragEvent<HTMLLIElement>, nodeType: string, component?: ComponentModel) => {
  if (event.dataTransfer != null) {
    event.dataTransfer.setData('application/nodeType', nodeType);
    if (component != null) {
      event.dataTransfer.setData('application/component', JSON.stringify(component))
    }
    event.dataTransfer.effectAllowed = 'move';
  }
};

const groupIconsMapper: Record<string, React.ReactNode> = {
  STRUCTURED_QUERY: <AppstoreOutlined />,
  PROMPT_QUERY: <FormOutlined />,
  CODERS: <CodeOutlined />,
  EXTRACTORS: <GlobalOutlined />,
  VECTORIZERS: <InsertRowBelowOutlined />,
  VECTOR_STORES: <DatabaseOutlined />,
  RETRIEVERS: <FileSearchOutlined />,
  SIMPLIFICATION: <BulbOutlined />,
  OUTPUT: <FileDoneOutlined />,
  NLP: <MessageOutlined />,
  SEARCH_ENGINES: <SearchOutlined />,
  MISCELLANEOUS: <EllipsisOutlined />,
  INPUT: <LoginOutlined />,
  TRANSFORMATIONS: <FormOutlined />,
  CONNECTORS: <ApiOutlined />,
  CUSTOM: <FormOutlined />
}

const generateItems = (groupedComponents: Record<string, ComponentModel[]>) => {
  const items = Object.keys(groupedComponents).map((groupKey, index) => {
    const group = groupedComponents[groupKey]
    const groupByClassName = _.groupBy(group, 'className')
    return getItem(
      group.length > 0
        ? group[0].group.toLocaleLowerCase().split('_')
          .map(word => word.charAt(0).toLocaleUpperCase() + word.slice(1)).join(' ')
        : 'Undefined',
      index.toString(),
      groupIconsMapper[groupKey] ?? groupIconsMapper['Miscellaneous'],
      generateLeafItems(
        groupByClassName,
        index.toString()
      )
    )
  })
  items.push({ type: 'divider' })
  return items
}

const generateLeafItems = (groupedComponents: Record<string, ComponentModel[]>, groupIndex: string) => {
  const result: MenuItem[] = []
  Object.keys(groupedComponents).forEach((cardType, typeIndex) => result.push(
    ...groupedComponents[cardType]?.map((component, index) => {
      return getItem(
        component.name,
        `${groupIndex}.${typeIndex}.${index}`,
        undefined,
        undefined,
        component,
      )
    })
  ))
  return result
}

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
  component?: ComponentModel
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
    component: component?.className,
    onDragStart: children === undefined
      ? (event: React.DragEvent<HTMLLIElement>) => onDragStart(
        event,
        component?.className ?? 'custom',
        component,)
      : undefined,
    draggable: children === undefined
  } as MenuItem;
}

const Sidebar: React.FC = () => {
  const [allSidebarItems, setAllSidebarItems] = useState<MenuProps['items']>([])
  const [sidebarItems, setSidebarItems] = useState<MenuProps['items']>([])
  const { components } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const userId = useUserId()

  const loadComponents = useCallback(() => {
    const groupedComponents: Record<string, ComponentModel[]> = _.groupBy(components, 'group')
    const items = generateItems(groupedComponents)
    setSidebarItems(items)
    setAllSidebarItems(items)
  }, [components])

  useEffect(() => {
    loadComponents()
  }, [loadComponents])

  //TODO: Add feedback
  if (!userId) return <></>

  const search = async (value: string) => {
    searchComponentsAction(value, userId)
      .then((result) => {
        if (value.length === 0) {
          setSidebarItems(allSidebarItems)
        } else {
          setSidebarItems(result.map((component, index) => {
            return getItem(
              component.name,
              index,
              undefined,
              undefined,
              component,
            )
          }))
        }
      })
      .catch(error => console.error(error))
  }

  return <Sider width={280} style={{ background: '#fff' }}>
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Input
        variant="borderless"
        placeholder="Search components..."
        prefix={<SearchOutlined style={{ marginRight: 6 }} />}
        onChange={(event) => search(event.target.value)}
        style={{
          paddingLeft: 24,
          margin: "12px 4px 4px 4px"
        }} />
      <Divider style={{ margin: "8px 0px" }} />
      <div style={{ flexGrow: 1, overflow: 'scroll' }}>
        <Menu
          mode="inline"
          style={{ height: '100%' }}
          items={sidebarItems}
          selectable={false}
        />
      </div>
    </div>
  </Sider>
}

export default Sidebar
