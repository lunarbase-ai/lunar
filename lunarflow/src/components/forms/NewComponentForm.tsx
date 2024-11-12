// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { ComponentDataType, ComponentModel, isComponentModel } from "@/models/component/ComponentModel"
import { CloseOutlined, SettingOutlined } from "@ant-design/icons"
import { Button, Form, Input, Layout, Modal, Select, Space, Spin, Typography, message } from "antd"
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
import { codeCompletionAction } from "@/app/actions/codeCompletion";

const { Item, List } = Form
const { Option } = Select
const { Content } = Layout
const { Text } = Typography

interface FieldInput {
  input_name: string;
  input_type: string;
  input_value: string;
}

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
  const [isModalOpen, setIsModalOpen] = useState<boolean>()

  const [code, setCode] = useState<string>('')
  const router = useRouter()

  const isExistingComponent = !!id

  useEffect(() => {
    if (isModalOpen === undefined) {
      setIsModalOpen(true)
    }
  }, [isModalOpen])

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
      componentCode: code,
      componentCodeRequirements: values["code_dependencies"],
      invalidErrors: [],
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
    try {
      const code = form.getFieldValue('code') ?? ''
      const completion = await codeCompletionAction(code)
      form.setFieldValue('code', completion)
      setCode(completion)
    } catch (e) {
      const errorDetail = e as AxiosError<{ detail: string }>
      messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
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

  const setCodeHeaderAfterInputUpdate = () => {
    const inputs: FieldInput[] = form.getFieldValue('input_types') ?? []
    const inputNames: string[] = ['self', ...inputs.map(input => input.input_name)]
    const newDeclaration = `def run(${inputNames.join(', ')}):`
    const regex = /def\s+run\([^\)]*\)\s*:/;
    const newCode = code.replace(regex, newDeclaration)
    form.setFieldValue('code', newCode)
    setCode(newCode)
  }

  const handleCodeChange = (value: string) => {
    form.setFieldValue('code', value)
    setCode(value)
  }


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
      onFinish={onFinish}
    >
      <Modal
        title="Component settings"
        open={isModalOpen}
        onOk={async () => {
          try {
            await form.validateFields()
            setCodeHeaderAfterInputUpdate()
            setIsModalOpen(false)
          } catch {
            console.log('>>>AAAAa')
          }
        }}
        onCancel={() => setIsModalOpen(false)}
        onClose={() => setIsModalOpen(false)}
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
          name="api-key"
          label="OpenAI api key"
        >
          <Input />
        </Item>
        <Item
          layout="vertical"
          name="endpoint"
          label="OpenAI Endpoint"
        >
          <Input />
        </Item>
      </Modal>
      <Space style={{ justifyContent: 'flex-end', paddingTop: 16, paddingRight: 16 }}>
        <Item>
          <Button
            icon={<SettingOutlined />}
            onClick={() => setIsModalOpen(true)}
          >
            Component Settings
          </Button>
        </Item>
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
            Add to My Library
          </Button>
        </Item>
        <Item>
          <Button type="primary" htmlType="submit">
            Publish
          </Button>
        </Item>
      </Space>
      <Content style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <CodeMirror
          value={code}
          onChange={handleCodeChange}
          extensions={[
            python(),
            // readOnlyRangesExtension((editorState) => readOnlyRanges)
          ]}
          style={{
            backgroundColor: "#fff",
            height: "100%",
            minHeight: 300,
            fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
          }}
        />
        <Space style={{ marginBottom: 16, marginLeft: 16 }}>
          <Text strong>Output:</Text>
          <Text>{runResult?.output.value ?? 'None'}</Text>
        </Space>
      </Content>
    </Form>
  </>
}

export default NewComponentForm
