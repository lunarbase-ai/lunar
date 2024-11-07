// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { SessionProvider, useSession } from "next-auth/react"
import { Button, Layout, message, Space, Spin, Typography } from "antd"
import { CaretRightFilled, SettingOutlined } from "@ant-design/icons"
import NewComponentModal from "../newComponentModal/newComponentModal"
import { useEffect, useState } from "react"
import { ComponentModel, isComponentModel } from '@/models/component/ComponentModel';
import { useUserId } from '@/hooks/useUserId';
import api from '@/app/api/lunarverse';
import { getComponentFromValues } from '../newComponentForm/formToComponent';
import { useRouter } from 'next/navigation';
import { Octokit } from "@octokit/rest";
import { AxiosError } from 'axios';

interface FieldInput {
  input_name: string;
  input_type: string;
  input_value: string;
}

interface Props {
  id?: string
  lunarverseOwner: string
  lunarverseRepository: string
}

const { Content } = Layout
const { Text } = Typography

const NewComponentContent: React.FC<Props> = ({ id, lunarverseOwner, lunarverseRepository }) => {

  const [isModalOpen, setIsModalOpen] = useState<boolean>()
  const [messageApi, contextHolder] = message.useMessage()
  const [runLoading, setRunLoading] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [runResult, setRunResult] = useState<ComponentModel>()
  const [completionLoading, setCompletionLoading] = useState<boolean>(false)
  const [publishLoading, setPublishLoading] = useState<boolean>(false)
  const [component, setComponent] = useState<ComponentModel | null>(null)
  const [code, setCode] = useState<string>('')
  const [documentation, setDocumentation] = useState<string>('')
  const session = useSession()
  const router = useRouter()
  const userId = useUserId()

  useEffect(() => {
    if (isModalOpen === undefined) {
      setIsModalOpen(true)
    }
  }, [])


  const codeCompletion = async () => {
    setCompletionLoading(true)
    if (code.includes('##')) {
      try {
        const { data: completion } = await api.post<string>('/code-completion', {
          code: code,
        })
        setCode(completion)
      } catch (e) {
        const errorDetail = e as AxiosError<{ detail: string }>
        messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
      }
    }
    setCompletionLoading(false)
  }

  const saveComponent = () => {
    api.post(`/component?user_id=${userId}`, component).then(response => {
      messageApi.success("Your component has been saved!", 1.5, () => {
        router.push('/home/components')
      })
    }).catch((error) => {
      console.error(error)
      messageApi.error("Failed to save component. Try again later")
    })
  }

  const handleCodeChange = (value: string) => {
    setCode(value)
    const componentCopy = component ? { ...component } : null
    if (componentCopy) componentCopy.componentCode = value
    setComponent(componentCopy)
  }

  const run = () => {
    setRunLoading(true)
    messageApi.destroy()
    api.post<ComponentModel | Record<string, string>>(`/component/run?user_id=${userId}`, component)
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
  }

  const getComponentCode = (runCode: string, component: ComponentModel) => {

    const inputs = '{' + component.inputs.map(input => `"${input.key}": DataType.${input.dataType}`).join(', ') + '}'
    const configuration = component.configuration
    const settings = Object.keys(configuration).map(conf => `${conf}="${configuration[conf]}",\n  `)

    const componentClassDefinition = `from typing import Any, Optional

from lunarcore.core.component import BaseComponent
from lunarcore.core.typings.components import ComponentGroup
from lunarcore.core.data_models import ComponentInput, ComponentModel
from lunarcore.core.typings.datatypes import DataType

class AzureOpenAIPrompt(
  BaseComponent,
  component_name="${component.name}",
  component_description="""${component.description}""",
  input_types=${inputs},
  output_type=DataType.${component.output.dataType},
  component_group=ComponentGroup.${component.group},
  ${settings}
):
  def __init__(self, model: Optional[ComponentModel] = None, **kwargs: Any):
    super().__init__(model=model, configuration=kwargs)

${runCode.split('\n').map(line => '  ' + line).join('\n')}
`
    return componentClassDefinition
  }

  const handlePublish = async () => {
    setPublishLoading(true)
    if (session.data?.provider !== "github") {
      router.push('/')
    }

    if (!component) {
      setPublishLoading(false)
      message.error("Fail to create pull request!")
      return
    }

    if (!component.name) {
      setPublishLoading(false)
      message.error("Component name is mandatory!")
      return
    }

    const octokit = new Octokit({
      auth: session.data?.accessToken,
    });

    try {

      const default_branch = 'development'

      const branchName = `${userId}/${component.name.replaceAll(' ', '_').toLowerCase()}-${new Date().getTime()}`;

      const { data: { object: { sha: latestCommitSha } } } = await octokit.git.getRef({
        owner: lunarverseOwner,
        repo: lunarverseRepository,
        ref: `heads/${default_branch}`,
      });

      await octokit.git.createRef({
        owner: lunarverseOwner,
        repo: lunarverseRepository,
        ref: `refs/heads/${branchName}`,
        sha: latestCommitSha,
      });

      await octokit.repos.createOrUpdateFileContents({
        owner: lunarverseOwner,
        repo: lunarverseRepository,
        path: `${component?.name.replaceAll(' ', '_').toLowerCase()}/__init__.py`,
        message: "Component submission",
        content: Buffer.from(getComponentCode(code, component)).toString("base64"),
        branch: branchName,
      });

      if (documentation !== '') {
        await octokit.repos.createOrUpdateFileContents({
          owner: lunarverseOwner,
          repo: lunarverseRepository,
          path: `${component?.name.replaceAll(' ', '_').toLowerCase()}/README.md`,
          message: "New Component documentation",
          content: Buffer.from(documentation).toString("base64"),
          branch: branchName,
        })
      }

      await octokit.pulls.create({
        owner: lunarverseOwner,
        repo: lunarverseRepository,
        title: `Code submission ${branchName}`,
        head: branchName,
        base: default_branch,
      });

      message.success("PR Created Successfully!");
    } catch (error) {
      console.error("Failed to create PR:", error);
      message.error("Something went wrong!");
    }
    setPublishLoading(false)
  }

  const setCodeHeaderAfterInputUpdate = (values: any) => {
    const inputs: FieldInput[] = values['input_types'] ?? []
    const inputNames: string[] = ['self', ...inputs.map(input => input.input_name)]
    const newDeclaration = `def run(${inputNames.join(', ')}):`
    const regex = /def\s+run\([^\)]*\)\s*:/;
    const matches = code.match(regex)
    if (!matches) {
      setCode(newDeclaration)
    } else {
      const newCode = code.replace(regex, newDeclaration)
      setCode(newCode)
    }
  }

  if (isLoading) return <Spin fullscreen />

  return <>
    {contextHolder}
    <NewComponentModal
      id={id}
      open={isModalOpen ?? false}
      onCancel={() => setIsModalOpen(false)}
      onClose={() => setIsModalOpen(false)}
      onFinish={(values) => {
        setComponent(getComponentFromValues(values, code, id))
        setCodeHeaderAfterInputUpdate(values)
        setDocumentation(values['documentation'])
        setIsModalOpen(false)
      }}
    />
    <Space style={{ justifyContent: 'space-between', alignItems: 'center', paddingTop: 16, paddingRight: 16, paddingLeft: 16 }}>
      <Space>
        <Typography.Title level={4} style={{ margin: 0 }}>
          {component?.name ?? "New Component"}
        </Typography.Title>
      </Space>
      <Space style={{ justifyContent: 'flex-end', alignItems: 'center' }}>
        <Button
          icon={<SettingOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          Component Settings
        </Button>
        <Button
          key="run"
          icon={<CaretRightFilled style={{ fontSize: 16 }} />}
          loading={runLoading}
          onClick={run}
        >
          Run
        </Button>
        <Button
          key="completion"
          loading={completionLoading}
          onClick={codeCompletion}
        >
          Code completion
        </Button>
        <Button type="primary" onClick={saveComponent}>
          Add to My Library
        </Button>
        <Button onClick={handlePublish} type="primary" loading={publishLoading}>
          Publish
        </Button>
      </Space>
    </Space>
    <Content style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      <CodeMirror
        value={code}
        onChange={handleCodeChange}
        extensions={[
          python()
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
  </>
}

const NewComponent: React.FC<Props> = ({ id, lunarverseOwner, lunarverseRepository }) => {
  return <SessionProvider>
    <NewComponentContent
      id={id}
      lunarverseOwner={lunarverseOwner}
      lunarverseRepository={lunarverseRepository}
    />
  </SessionProvider>
}

export default NewComponent
