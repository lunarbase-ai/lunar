// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { useUserId } from "@/hooks/useUserId";
import { EnvironmentVariable } from "@/models/environmentVariable"
import { DeleteOutlined } from "@ant-design/icons";
import { Button, Form, Input, Modal, Table, TableProps } from "antd"
import React, { useState } from "react"
import SecretDisplay from "../secret/secretDisplay";
import { setEnvironmentVariablesAction } from "@/app/actions/environmentVariables";
import { useRouter } from "next/navigation";

type EnvironmentVariableFormType = {
  variable?: string;
  value?: string;
};

interface EnvironmentListProps {
  environmentVariables: EnvironmentVariable[]
}

const EnvironmentList: React.FC<EnvironmentListProps> = ({
  environmentVariables
}) => {
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false)
  const router = useRouter()
  const userId = useUserId()

  const columns: TableProps<EnvironmentVariable>['columns'] = [{
    key: 'variable',
    title: 'Variable',
    render: (_, environmentVariable) => <p>{environmentVariable.variable}</p>
  }, {
    key: 'value',
    title: 'Value',
    width: 300,
    render: (_, environmentVariables) => <SecretDisplay secret={environmentVariables.value} />
  }, {
    key: 'actions',
    title: '',
    width: 40,
    render: (_, environmentVariable) => <div>
      <Button icon={<DeleteOutlined />} type="text" onClick={() => removeEnvironmentVariable(environmentVariable.variable)}></Button>
    </div>
  }]

  const addNewEnvironmentVariable = async ({ variable, value }: { variable: string, value: string }) => {
    if (!userId) return
    const envVars: Record<string, string> = {}
    environmentVariables.forEach(variable => {
      envVars[variable.variable] = variable.value
    })
    envVars[variable.toUpperCase()] = value
    await setEnvironmentVariablesAction(envVars, userId)
    router.refresh()
    setIsModalOpen(false)
  }

  const removeEnvironmentVariable = async (variable: string) => {
    if (!userId) return
    const newEnvVars: Record<string, string> = {}
    environmentVariables.forEach(envVar => {
      if (envVar.variable !== variable) newEnvVars[envVar.variable] = envVar.value
    })
    await setEnvironmentVariablesAction(newEnvVars, userId)
    router.refresh()
  }

  return <>
    <Modal
      title='Create new environment variable'
      open={isModalOpen}
      onCancel={() => setIsModalOpen(false)}
      onClose={() => setIsModalOpen(false)}
      footer={<></>}
    >
      <Form
        name="variable"
        layout="vertical"
        style={{ paddingTop: 16 }}
        onFinish={addNewEnvironmentVariable}
      >
        <Form.Item<EnvironmentVariableFormType>
          name='variable'
          label='Variable'
          rules={[{ required: true, message: 'Variable is required!' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item<EnvironmentVariableFormType>
          name='value'
          label='Value'
          rules={[{ required: true, message: 'Value is required!' }]}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item
          wrapperCol={{ style: { display: 'flex' } }}
        >
          <Button type="primary" htmlType="submit" style={{ marginLeft: 'auto' }}>
            Create
          </Button>
        </Form.Item>
      </Form>
    </Modal>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 32, marginBottom: 16 }}>
      <h2 style={{
        fontSize: 24,
        fontWeight: 'bold',
        color: '#0D181C',
      }}>
        Environment variables
      </h2>
      <Button onClick={() => setIsModalOpen(true)}>Add variable</Button>
    </div>
    <Table columns={columns} dataSource={environmentVariables} />
  </>
}

export default EnvironmentList
