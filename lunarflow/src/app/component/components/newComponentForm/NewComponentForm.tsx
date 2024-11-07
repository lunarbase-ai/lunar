// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { ComponentDataType, ComponentModel } from "@/models/component/ComponentModel"
import { CloseOutlined } from "@ant-design/icons"
import {
  Button,
  Form,
  Input,
  Select,
  Space,
  message
} from "antd"
import api from "@/app/api/lunarverse";
import { useUserId } from "@/hooks/useUserId";
import { useEffect, useState } from "react";
import { useForm } from "antd/es/form/Form";
import { getFormValues } from "./formToComponent";
import './new-component-form.css'


const { Item, List } = Form
const { Option } = Select

interface Props {
  id?: string
  onFinish?: ((values: any) => void)
}

const NewComponentForm: React.FC<Props> = ({ id, onFinish }) => {

  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [form] = useForm()
  const [messageApi, contextHolder] = message.useMessage()
  const userId = useUserId()


  const isExistingComponent = !!id

  useEffect(() => {
    if (isExistingComponent && userId) {
      setIsLoading(true)
      api.get<ComponentModel>(`/component/${id}?user_id=${userId}`)
        .then(({ data: component }) => {
          form.setFieldsValue(getFormValues(component))
        })
        .catch(error => {
          messageApi.destroy()
          messageApi.error({
            content: error?.message ?? "Failed to load component",
            onClick: () => messageApi.destroy()
          }, 0)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [id, userId])

  return <>
    {contextHolder}
    <Form
      form={form}
      layout="vertical"
      style={{
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        height: '100%',
      }}
      onFinish={async (values) => {
        try {
          await form.validateFields()
          if (onFinish) onFinish(values)
        } catch (error) {
          console.error(error)
        }
      }}
    >
      <Item
        layout="vertical"
        name="component_name"
        label="Component name"
        style={{ marginTop: 16 }}
        rules={[{ required: true, message: 'Please add a component name!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="component_description"
        label="Component description"
        rules={[{ required: true, message: 'Please add a component description!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        label="Inputs"
      >
        <List name="input_types">
          {(fields, { add, remove }) => (<div style={{ display: 'flex', flexDirection: 'column', rowGap: 16 }}>
            {fields.map((field) => (
              <Space key={field.key}>
                <Item
                  noStyle
                  name={[field.name, 'input_name']}
                  rules={[{ required: true, message: 'Please add an input name!' }]}
                >
                  <Input placeholder="Input name" />
                </Item>
                <Item
                  noStyle
                  name={[field.name, 'input_type']}
                  rules={[{ required: true, message: 'Please add an input type!' }]}
                >
                  <Select style={{ minWidth: '200px' }}>
                    {Object.values(ComponentDataType).map(dataType => <Option key={dataType} value={dataType}>
                      {dataType}
                    </Option>)}
                  </Select>
                </Item>
                <Item
                  noStyle
                  name={[field.name, 'input_value']}
                >
                  <Input placeholder="Input value" />
                </Item>
                <CloseOutlined
                  onClick={() => {
                    remove(field.name);
                  }}
                />
              </Space>
            ))}
            <Button type="dashed" onClick={() => add()} block>
              + Add Input
            </Button>
          </div>)}
        </List>
      </Item>
      <Item
        layout="vertical"
        name="output_type"
        label="Output type"
        rules={[{ required: true, message: 'Please add an output type!' }]}
      >
        <Select placeholder="Input type">
          {Object.values(ComponentDataType).map(dataType => <Option key={dataType} value={dataType}>
            {dataType}
          </Option>)}
        </Select>
      </Item>
      <Item
        layout="vertical"
        name="component_group"
        label="Component Group"
        initialValue="Custom"
        rules={[{ required: true, message: 'Please add a component group!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        label="Configuration"
      >
        <List name="configuration">
          {(fields, { add, remove }) => (<div style={{ display: 'flex', flexDirection: 'column', rowGap: 16 }}>
            {fields.map((field) => (
              <Space key={field.key}>
                <Item
                  noStyle
                  name={[field.name, 'name']}
                  rules={[{ required: true, message: 'Please add a configuration name!' }]}
                >
                  <Input placeholder="Name" />
                </Item>
                <Item
                  noStyle
                  name={[field.name, 'value']}
                >
                  <Input placeholder="Value" />
                </Item>
                <CloseOutlined
                  onClick={() => {
                    remove(field.name);
                  }}
                />
              </Space>
            ))}
            <Button type="dashed" onClick={() => add()} block>
              + Add Configuration
            </Button>
          </div>)}
        </List>
      </Item>
      <Item
        name="code_dependencies"
        layout="vertical"
        label="Code dependencies"
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="documentation"
        label="README.md Documentation"
      >
        <Input.TextArea />
      </Item>
      <Button type="primary" htmlType="submit">
        Ok
      </Button>
    </Form>
  </>
}

export default NewComponentForm
