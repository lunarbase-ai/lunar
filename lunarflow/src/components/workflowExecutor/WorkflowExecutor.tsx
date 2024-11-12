// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import Logo from '@/assets/Brand.png';
import { Header } from "@/lib/layout"
import { Workflow } from "@/models/Workflow"
import { Alert, Button, Form, Layout, Space, Typography } from "antd"
import Image from 'next/image';
import { SessionProvider } from "next-auth/react"
import AvatarDropdown from '../AvatarDropdown';
import { useRouter } from 'next/navigation';
import { getWorkflowInputs, getWorkflowOutputLabel } from '@/utils/workflows';
import GenericInput from '../io/GenericInput/GenericInput';
import { Fragment, ReactNode, useEffect, useState } from 'react';
import { ComponentModel } from '@/models/component/ComponentModel';
import GenericOutput from '../io/GenericOutput/GenericOutput';
import useForm from 'antd/es/form/hooks/useForm';
import { ReactFlowProvider } from 'reactflow';
import ExecutorButton from './ExecutorButton';
import { ComponentInput } from '@/models/component/ComponentInput';

const { Title } = Typography

interface Props {
  workflow: Workflow
  redirectToWorkflow: (workflowId: string) => void
}

const WorkflowExecutor: React.FC<Props> = ({ workflow, redirectToWorkflow }) => {
  const [updatedWorkflow, setUpdatedWorkflow] = useState<Workflow>(workflow)
  const [componentResults, setComponentResults] = useState<Record<string, ComponentModel>>({})
  const [errors, setErrors] = useState<string[]>([])
  const [parameters, setParameters] = useState<string[]>([])
  const { push } = useRouter()
  const [form] = useForm()



  const outputLabel = getWorkflowOutputLabel(workflow)
  const workflowInputs = getWorkflowInputs(workflow)

  useEffect(() => {
    Object.keys(workflowInputs).forEach(componentKey => {
      workflowInputs[componentKey].forEach(input => {
        form.setFieldValue(`${componentKey}:${input.key}`, input.value)
      })
    })
    const workflowOutput = workflow.components.find(component => component.label === outputLabel)
    if (workflowOutput && outputLabel) {
      const componentResult: Record<string, ComponentModel> = {}
      componentResult[outputLabel] = workflowOutput
      setComponentResults(componentResult)
    }
  }, [])

  const renderFormItems = (workflowInputs: Record<string, ComponentInput[]>) => {
    let formItems: ReactNode[] = []
    Object.keys(workflowInputs).forEach(workflowInputKey => {
      formItems = [...formItems, workflowInputs[workflowInputKey].map((input, index) => <Fragment key={index}>
        <Form.Item
          key={index}
          label={`${workflowInputKey}:${input.key}`}
          labelAlign="left"
          required
        >
          <GenericInput
            inputKey={`${workflowInputKey}:${input.key}`}
            value={form.getFieldValue(`${workflowInputKey}:${input.key}`)}
            inputType={input.dataType}
            onInputChange={(inputKey, inputValue) => {

              setUpdatedWorkflow(workflow => {
                const copy: Workflow = structuredClone(workflow)
                const componentLabel = input.key.split(':').at(0)
                const inputKeySplit = input.key.split(':').at(-1)?.split('$')
                const inputKey = inputKeySplit?.at(0)
                const workflowInput = copy.components
                  .find(component => component.id === input.componentId || component.label === componentLabel)?.inputs
                  .find(componentInput => componentInput.key === inputKey)
                if (inputKeySplit && inputKeySplit?.length > 1) {
                  const templateVariableKey = inputKeySplit.at(-1) as string
                  if (workflowInput?.templateVariables != null) workflowInput.templateVariables[`${inputKey}.${templateVariableKey}`] = inputValue
                } else if (workflowInput?.value != null) workflowInput.value = inputValue
                return copy
              })
              form.setFieldValue(`${workflowInputKey}:${input.key}`, inputValue)
            }}
            setParameters={setParameters}
          />
        </Form.Item>
      </Fragment>)]
    })
    return formItems
  }

  return <SessionProvider>
    <ReactFlowProvider>
      <Layout style={{ height: '100%', backgroundColor: '#fff' }}>
        <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Image
            src={Logo}
            width={125}
            height={32}
            alt='Lunar'
            style={{ verticalAlign: 'middle', cursor: 'pointer' }}
            onClick={() => push('/')}
          />
          <AvatarDropdown />
        </Header>
        <Layout
          style={{
            backgroundColor: '#fff'
          }}
        >
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            maxWidth: 800,
            width: '100%',
            flexGrow: 1,
            marginTop: 32,
            marginRight: 'auto',
            marginLeft: 'auto',
            gap: 8,
            backgroundColor: '#fff'
          }}
          >
            <Space style={{
              justifyContent: 'space-between',
            }}>
              <Title level={2} style={{ margin: 0 }}>{workflow.name}</Title>
              <Space.Compact
                style={{ padding: 8, width: '100%' }}
              >
                <ExecutorButton
                  workflow={updatedWorkflow}
                  setComponentResults={setComponentResults}
                  setErrors={setErrors}
                />
                <Button
                  onClick={() => redirectToWorkflow(workflow.id)}
                >
                  Edit workflow
                </Button>
              </Space.Compact>
            </Space>
            <Form
              form={form}
              layout='vertical'
            >
              {errors.map((error, index) => <Alert
                key={index}
                message={error}
                type="error"
                showIcon
                style={{ marginBottom: 16 }}
                closable
              />)}
              {renderFormItems(workflowInputs)}
            </Form>
            {outputLabel && componentResults[outputLabel] ? <GenericOutput
              key={outputLabel}
              workflowId={workflow.id}
              outputDataType={componentResults[outputLabel].output.dataType}
              content={componentResults[outputLabel].output.value}
            /> : <></>}
            {/* {Object.keys(componentResults).map(resultKey => <GenericOutput
            key={resultKey}
            workflowId={workflow.id}
            outputDataType={componentResults[resultKey].output.dataType}
            content={componentResults[resultKey].output.value}
          />)} */}

          </div>
        </Layout>
      </Layout>
    </ReactFlowProvider>
  </SessionProvider>
}

export default WorkflowExecutor
