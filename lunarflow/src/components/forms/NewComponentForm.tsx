// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { ComponentDataType, ComponentModel, isComponentModel } from "@/models/component/ComponentModel"
import { CloseOutlined } from "@ant-design/icons"
import { Button, Form, Input, Layout, Select, Space, Spin, Typography, message } from "antd"
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import './new-component-form.css'
import { ComponentInput } from "@/models/component/ComponentInput";
import api from "@/app/api/lunarverse";
import { useUserId } from "@/hooks/useUserId";
import { useEffect, useState } from "react";
import { useForm } from "antd/es/form/Form";
import { AxiosError } from "axios";
import { useRouter } from "next/navigation";


const { Item, List } = Form
const { Option } = Select
const { Content, Sider } = Layout
const { Text } = Typography

interface Props {
  id?: string
}

const NewComponentForm: React.FC<Props> = ({ id }) => {

  const userId = useUserId()
  const [form] = useForm()
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [completionLoading, setCompletionLoading] = useState<boolean>(false)
  const [runLoading, setRunLoading] = useState<boolean>(false)
  const [messageApi, contextHolder] = message.useMessage()
  const [runResult, setRunResult] = useState<ComponentModel>()
  const router = useRouter()

  const isExistingComponent = !!id

  useEffect(() => {
    if (isExistingComponent && userId) {
      setIsLoading(true)
      api.get<ComponentModel>(`/component/${id}?user_id=${userId}`)
        .then(({ data: component }) => {
          form.setFieldsValue(getFormValues(component))
          setIsLoading(false)
        })
        .catch(error => {
          messageApi.destroy()
          messageApi.error({
            content: error?.message ?? "Failed to load component",
            onClick: () => messageApi.destroy()
          }, 0)
          setIsLoading(false)
        })
    }
  }, [id, userId])

  const getFormValues = (component: ComponentModel) => {
    const inputs = component?.inputs.map(input => ({ input_name: input.key, input_type: input.dataType }))
    const currentConfiguration = component?.configuration
    const configuration = component ? Object.keys(currentConfiguration).map(conf => ({ name: conf, value: currentConfiguration[conf] })) : []
    return {
      component_name: component?.name,
      component_description: component?.description,
      component_group: component?.group,
      input_types: inputs,
      output_type: component?.output.dataType,
      configuration: configuration,
      code: component?.componentCode,
      code_dependencies: component?.componentCodeRequirements || []
    }
  }

  const getComponentFromValues = (values: any) => {
    const inputTypes: { input_name: string, input_type: string, input_value?: string }[] | undefined = values["input_types"]
    const newInputs = inputTypes?.map(input => {
      const newInput: ComponentInput = {
        key: input.input_name,
        value: input.input_value,
        dataType: ComponentDataType[input.input_type as keyof typeof ComponentDataType],
        templateVariables: {},
        componentId: id ?? null,
      }
      return newInput
    })
    const newConfig: Record<string, string> = {}
    const configuration: { name: string, value: string }[] | undefined = values["configuration"]
    configuration?.forEach(config => {
      newConfig[config.name] = config.value
    })
    const newComponentModel: ComponentModel = {
      id: id,
      name: values["component_name"],
      className: "Custom",
      description: values["component_description"],
      group: values["component_group"],
      inputs: newInputs || [],
      output: {
        key: "",
        value: undefined,
        dataType: values["output_type"]
      },
      configuration: newConfig,
      isCustom: true,
      isTerminal: false,
      componentCode: values["code"] || null,
      componentCodeRequirements: values["code_dependencies"],
      invalidErrors: []
    }
    return newComponentModel
  }

  const run = () => {
    messageApi.destroy()
    form.validateFields()
      .then(values => {
        const newComponentModel = getComponentFromValues(values)
        setRunLoading(true)
        api.post<ComponentModel | Record<string, string>>(`/component/run?user_id=${userId}`, newComponentModel)
          .then((result) => {
            Object.values(result.data).forEach(resultData => {
              if (!isComponentModel(resultData)) {
                messageApi.error({
                  content: resultData,
                  onClick: () => messageApi.destroy()
                }, 0)
              } else {
                setRunResult(resultData as ComponentModel)
              }
            })
          })
          .catch(error => {
            messageApi.error({
              content: error?.message ?? "Failed to run the new component",
              onClick: () => messageApi.destroy()
            }, 0)
          })
          .finally(() => {
            setRunLoading(false)
          })
      })
      .catch(error => {
        messageApi.error({
          content: error?.message ?? "Failed to validate the new component form",
          onClick: () => messageApi.destroy()
        }, 0)
      })

  }

  const codeCompletion = async () => {
    setCompletionLoading(true)
    const code = form.getFieldValue('code')
    if (code.includes('##')) {
      try {
        const { data: completion } = await api.post<string>('/code-completion', {
          code: code,
          key: form.getFieldValue('api-key'),
          base: form.getFieldValue('endpoint')
        })
        form.setFieldValue('code', completion)
      } catch (e) {
        const errorDetail = e as AxiosError<{ detail: string }>
        messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
      }
    }
    setCompletionLoading(false)
  }

  const onFinish = (values: any) => {
    const newComponentModel = getComponentFromValues(values)
    api.post(`/component?user_id=${userId}`, newComponentModel).then(response => {
      messageApi.success("Your component has been saved!", 1.5, () => {
        router.push('/home/components')
      })
    }).catch((error) => {
      console.error(error)
      messageApi.error("Failed to save component. Try again later")
    })
  }

  if (isLoading) return <Spin fullscreen />

  return <>
    {contextHolder}
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        code: `def run(
          self, inputs, **kwargs
        ):
          return True`
      }}
      style={{
        padding: '40px 0 0 0',
        display: 'flex',
        flexGrow: 1,
        height: '100%',
      }}
      onFinish={onFinish}
    >
      <Sider width="40%" style={{
        marginRight: 16,
        backgroundColor: 'transparent',
        padding: "0 40px",
        overflowY: "scroll",
        marginBottom: 40
      }}>
        <Item
          name="component_name"
          label="Component name"
          rules={[{ required: true, message: 'Please add a component name!' }]}
        >
          <Input />
        </Item>
        <Item
          name="component_description"
          label="Component description"
          rules={[{ required: true, message: 'Please add a component description!' }]}
        >
          <Input />
        </Item>
        <Item label="Inputs">
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
          name="component_group"
          label="Component Group"
          initialValue="Miscellaneous"
          rules={[{ required: true, message: 'Please add a component group!' }]}
        >
          <Input />
        </Item>
        <Item label="Configuration">
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
          label="Code dependencies">
          <Input />
        </Item>
        <Item
          name="api-key"
          label="OpenAI api key"
        >
          <Input />
        </Item>
        <Item
          name="endpoint"
          label="OpenAI Endpoint"
        >
          <Input />
        </Item>
      </Sider>
      <Content style={{ paddingRight: 40, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Item
          name="code"
          label="Code"
          rules={[{ required: true, message: 'Please add the component code!' }]}
          style={{
            display: 'flex',
            alignItems: 'stretch',
            flexDirection: 'column',
            flexGrow: 1,
            height: "100%",
            width: "100%",
          }}
        >
          <CodeMirror
            extensions={[python()]}
            style={{
              backgroundColor: "#fff",
              height: "100%",
              minHeight: 300,
              fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
            }}
          />
        </Item>
        <Space style={{ marginBottom: 16 }}>
          <Text strong>Output:</Text>
          <Text>{runResult?.output.value ?? 'None'}</Text>
        </Space>
        <Space style={{ justifyContent: 'flex-end' }}>
          <Item>
            <Button
              key="run"
              loading={runLoading}
              onClick={run}
            >
              Run
            </Button>
          </Item>
          <Item>
            <Button
              key="completion"
              loading={completionLoading}
              onClick={codeCompletion}
            >
              Code completion
            </Button>
          </Item>
          <Item>
            <Button type="primary" htmlType="submit">
              Create component
            </Button>
          </Item>
        </Space>
      </Content>
    </Form>
  </>
}

export default NewComponentForm
