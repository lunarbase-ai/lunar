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
import { getComponentFromValues } from '../newComponentForm/formToComponent';
import { useRouter } from 'next/navigation';
import { AxiosError } from 'axios';
import { getComponentAction, runComponentAction, saveComponentAction } from '@/app/actions/components';
import { convertClientToComponentModel } from '@/utils/workflows';
import { generateComponentCodeAction, publishComponentAction } from '@/app/actions/componentPublishing';

interface FieldInput {
  input_name: string;
  input_type: string;
  input_value: string;
}

interface Props {
  id?: string
  lunarverseOwner: string
  lunarverseRepository: string
  codeCompletionAction: (code: string) => Promise<string>
  saveComponentAction: (component: ComponentModel, userId: string) => Promise<void>
}

const { Content } = Layout
const { Text } = Typography

const processConfiguration = (configurationArray: { name: string, value: string }[]) => {
  const configurationObject: Record<string, string> = {}
  configurationArray.forEach(configuration => {
    configurationObject[configuration.name] = configuration.value
  })
  return configurationObject
}

const NewComponentContent: React.FC<Props> = ({
  id,
  codeCompletionAction,
}) => {

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
  const [author, setAuthor] = useState<string>('')
  const [authorEmail, setAuthorEmail] = useState<string>('')
  const [version, setVersion] = useState<string>('')
  const session = useSession()
  const router = useRouter()
  const userId = useUserId()
  const isExistingComponent = !!id

  useEffect(() => {
    if (isExistingComponent && userId) {
      setIsLoading(true)
      getComponentAction(id, userId).then(component => {
        generateComponentCodeAction(component, userId).then(componentCode => {
          setCode(componentCode)
        })
        setComponent(component)
      })
        .catch(error => {
          //TODO: show feedback
          console.error(error)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [userId])

  useEffect(() => {
    if (isModalOpen === undefined && !isExistingComponent) {
      setIsModalOpen(true)
    }
  }, [])

  if (!userId) return <></>

  const codeCompletion = async () => {
    setCompletionLoading(true)
    try {
      const completion = await codeCompletionAction(code)
      setCode(completion)
    } catch (e) {
      const errorDetail = e as AxiosError<{ detail: string }>
      messageApi.error(`Failed to complete code: ${errorDetail.response?.data.detail}`)
    }
    setCompletionLoading(false)
  }

  const saveComponent = () => {
    if (component && userId) {
      saveComponentAction(convertClientToComponentModel(component), userId).then(() => {
        messageApi.success("Your component has been saved!", 1.5, () => {
          router.push('/home/components')
        })
      }).catch((error) => {
        console.error(error)
        messageApi.error("Failed to save component. Try again later")
      })
    } else {
      messageApi.error("Failed to save component. Component or userId is null")
    }
  }

  const extractRunMethod = (classString: string) => {
    const runMethodRegex = /def\s+run\s*\(.*\)\s*:\n(?:\s{4,}.*\n?)*/;

    const match = runMethodRegex.exec(classString);

    if (match) {
      const runMethod = match[0]
      return runMethod
    }

    return ""
  }

  const handleCodeChange = (value: string) => {
    setCode(value)
    const componentCopy = component ? { ...component } : null
    const runMethod = extractRunMethod(value)
    if (componentCopy) componentCopy.componentCode = runMethod
    setComponent(componentCopy)
  }

  const run = () => {
    messageApi.destroy()
    if (component && userId) {
      setRunLoading(true)
      runComponentAction(convertClientToComponentModel(component), userId)
        .then((result) => {
          Object.values(result).forEach(resultData => {
            if (!isComponentModel(resultData)) {
              messageApi.error({
                content: "Fail to run component!",
                onClick: () => messageApi.destroy()
              }, 0)
            } else {
              setRunResult(resultData as ComponentModel)
            }
          })
        })
        .catch(error => {
          console.error(error)
          messageApi.error({
            content: error?.message ?? "Failed to run the new component",
            onClick: () => messageApi.destroy()
          }, 0)
        })
        .finally(() => {
          setRunLoading(false)
        })
    }

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

    const accessToken = session.data?.accessToken

    if (!accessToken) {
      setPublishLoading(false)
      message.error("You need to be signed in with Github to publish components!")
      return
    }

    try {

      publishComponentAction({
        author: author,
        author_email: authorEmail,
        component_name: component.name,
        component_description: component.description,
        component_class: code,
        component_documentation: documentation,
        version: version,
        access_token: accessToken,
        user_id: userId,
      }, userId)

      // const default_branch = 'develop'

      // const branchName = `${userId}/${component.name.replaceAll(' ', '_').toLowerCase()}-${new Date().getTime()}`;

      // const { data: { object: { sha: latestCommitSha } } } = await octokit.git.getRef({
      //   owner: lunarverseOwner,
      //   repo: lunarverseRepository,
      //   ref: `heads/${default_branch}`,
      // });

      // await octokit.git.createRef({
      //   owner: lunarverseOwner,
      //   repo: lunarverseRepository,
      //   ref: `refs/heads/${branchName}`,
      //   sha: latestCommitSha,
      // });

      // await octokit.repos.createOrUpdateFileContents({
      //   owner: lunarverseOwner,
      //   repo: lunarverseRepository,
      //   path: `${component?.name.replaceAll(' ', '_').toLowerCase()}/__init__.py`,
      //   message: "Component submission",
      //   content: Buffer.from('').toString("base64"),
      //   branch: branchName,
      // });

      // if (documentation !== '') {
      //   await octokit.repos.createOrUpdateFileContents({
      //     owner: lunarverseOwner,
      //     repo: lunarverseRepository,
      //     path: `${component?.name.replaceAll(' ', '_').toLowerCase()}/README.md`,
      //     message: "New Component documentation",
      //     content: Buffer.from(documentation).toString("base64"),
      //     branch: branchName,
      //   })
      // }

      // await octokit.pulls.create({
      //   owner: lunarverseOwner,
      //   repo: lunarverseRepository,
      //   title: `Code submission ${branchName}`,
      //   head: branchName,
      //   base: default_branch,
      // });

      // message.success("PR Created Successfully!");
    } catch (error) {
      console.error("Failed to create PR:", error);
      message.error("Something went wrong!");
    }
    setPublishLoading(false)
  }

  const onFinish = async (values: any) => {
    const generatedComponent = getComponentFromValues(values, extractRunMethod(code), id)
    const componentClassCode = await generateComponentCodeAction(convertClientToComponentModel(generatedComponent), userId)
    setComponent(generatedComponent)
    setCode(componentClassCode)
    setDocumentation(values['documentation'])
    setAuthor(values['author'])
    setAuthorEmail(values['author_email'])
    setVersion(values['version'])
    setIsModalOpen(false)
  }

  if (isLoading) return <Spin fullscreen />

  return <>
    {contextHolder}
    <NewComponentModal
      id={id}
      open={isModalOpen ?? false}
      onCancel={() => setIsModalOpen(false)}
      onClose={() => setIsModalOpen(false)}
      onFinish={onFinish}
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

const NewComponent: React.FC<Props> = (props) => {
  return <SessionProvider>
    <NewComponentContent {...props} />
  </SessionProvider>
}

export default NewComponent
