// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { ComponentDataType } from "@/models/component/ComponentModel"
import { CloseOutlined } from "@ant-design/icons"
import {
  Button,
  Form,
  Input,
  Select,
  Space,
  Typography,
  message
} from "antd"
import { useUserId } from "@/hooks/useUserId";
import { useEffect, useState } from "react";
import { useForm } from "antd/es/form/Form";
import { getFormValues } from "./formToComponent";
import './new-component-form.css'
import { getComponentAction } from "@/app/actions/components";


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
      getComponentAction(id, userId)
        .then((component) => {
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
        tooltip="A human readable name for your component"
        style={{ marginTop: 16 }}
        rules={[{ required: true, message: 'Please add a component name!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="component_description"
        label="Component description"
        tooltip="A short description of your component's functionalities. It will be displayed in the UI."
        rules={[{ required: true, message: 'Please add a component description!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        label="Inputs"
        tooltip={<div>One of the supported lunar types. All available types can be found <Typography.Link href="https://lunarbase-ai.github.io/docs/component" target="_blank">here</Typography.Link>. The input value is for this development environment only. It will not be saved.</div>}
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
                  tooltip={<div>One of the supported lunar types. All available types can be found <Typography.Link href="https://lunarbase-ai.github.io/docs/component" target="_blank">here</Typography.Link></div>}
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
                  tooltip="The input value for the development environment only. It will not be saved."
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
        tooltip={<div>One of the supported lunar types. All available types can be found <Typography.Link href="https://lunarbase-ai.github.io/docs/component" target="_blank">here</Typography.Link></div>}
        rules={[{ required: true, message: 'Please add an output type!' }]}
      >
        <Select placeholder="Output type">
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
        tooltip="One of the supported lunar groups. If not provided, it will be custom"
        rules={[{ required: true, message: 'Please add a component group!' }]}
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        label="Configuration"
        tooltip="Specific configuration options for the component"
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
        tooltip="Comma separated python packages used by the component. They will be installed with pip."
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="documentation"
        label="README.md Documentation"
        tooltip="A markdown file for documentation. Please, include detailed information about your component here."
      >
        <Input.TextArea />
      </Item>
      <Item
        layout="vertical"
        name="author"
        label="Author"
        tooltip="The component author name"
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="author_email"
        label="Author Email"
      >
        <Input />
      </Item>
      <Item
        layout="vertical"
        name="version"
        label="Component Version"
        tooltip="The version of your component"
      >
        <Input />
      </Item>
      <Button type="primary" htmlType="submit">
        Ok
      </Button>
    </Form>
  </>
}

export default NewComponentForm
