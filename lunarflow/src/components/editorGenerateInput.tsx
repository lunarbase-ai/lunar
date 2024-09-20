import React, { SVGProps, useContext, useState } from 'react'
import { Button, Divider, Input } from 'antd'
import { getWorkflowFromView, loadWorkflow } from '@/utils/workflows'
import api from '@/app/api/lunarverse'
import { Workflow } from '@/models/Workflow'
import { useEdges, useNodes, useReactFlow } from 'reactflow'
import { useUserId } from '@/hooks/useUserId'
import { WorkflowEditorContext } from "@/contexts/WorkflowEditorContext"
import { WorkflowEditorContextType } from '@/models/workflowEditor/WorkflowEditorContextType'
import { ComponentModel } from '@/models/component/ComponentModel'
import Icon from '@ant-design/icons'

interface WorkflowHistoryItem {
  workflow: Workflow
  prompt: string
}

interface Props {
  workflowId: string
}

const MagicSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={16}
    height={16}
    fill="#FFFFFF"
    viewBox="0 0 24 24"
    {...props}
  >
    <path fill="none" d="M0 0h24v24H0z" />
    <path d="m19 9 1.25-2.75L23 5l-2.75-1.25L19 1l-1.25 2.75L15 5l2.75 1.25L19 9zm-7.5.5L9 4 6.5 9.5 1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5zM19 15l-1.25 2.75L15 19l2.75 1.25L19 23l1.25-2.75L23 19l-2.75-1.25L19 15z" />
  </svg>
)

const EditorGenerateInput: React.FC<Props> = ({ workflowId }) => {

  const [inputValue, setInputValue] = useState('')
  const [generationLoading, setGenerationLoading] = useState(false)
  const [generatedWorkflows, setGeneratedWorkflows] = useState<WorkflowHistoryItem[]>([])
  const { workflowEditor, setValues } = useContext(WorkflowEditorContext) as WorkflowEditorContextType
  const reactflowNodes = useNodes<ComponentModel>()
  const reactflowEdges = useEdges<null>()
  const instance = useReactFlow()
  const userId = useUserId()

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (event.target.value === '') {
      setShowSuggestions(true);
    }
    setInputValue(event.target.value)
  }

  const generateWorkflow = (instruction: string) => {
    setGenerationLoading(true)
    const currentWorkflow = getWorkflowFromView(workflowId, workflowEditor.name, workflowEditor.description, reactflowNodes, reactflowEdges, userId)
    api.post<Workflow>(`/auto_workflow_modification?user_id=${userId}&modification_instruction=${instruction}`, {
      workflow: currentWorkflow
    }).then((response) => {
      const newWorkflow = response.data
      loadWorkflow(instance, newWorkflow, setValues)
      setGeneratedWorkflows([...generatedWorkflows, { workflow: newWorkflow, prompt: instruction }])
    }).catch((error) => {
      console.error(error)
    }).finally(() => {
      setGenerationLoading(false)
    })
  }

  const [showSuggestions, setShowSuggestions] = useState(true);

  const handleSuggestionClick = (prompt: string) => {
    setInputValue(prompt);
    setShowSuggestions(false);
  };

  return (
    <div style={{
      marginTop: 16,
      marginBottom: 16,
      marginRight: 24,
      marginLeft: 24,
      display: 'flex',
      alignItems: 'flex-end',
      flex: '1 1',
      justifyContent: 'flex-start',
      flexDirection: 'column'
    }}>
      <h2 style={{ width: '100%', marginBottom: 16 }}>Generate</h2>
      <Input.TextArea
        value={inputValue}
        onChange={handleInputChange}
        placeholder="Generate a Lunar workflow"
        style={{
          marginBottom: 8,
          height: showSuggestions ? 80 : 80 + 128,
          maxHeight: 80 + 128,
        }}
      />
      {showSuggestions && (
        <div style={{ marginTop: 8, marginBottom: 8, width: '100%' }}>
          <Button
            type="default"
            style={{ width: '100%', marginBottom: 8, whiteSpace: "normal", height: 'auto' }}
            onClick={() => handleSuggestionClick('Connect the output to a Report component')}
          >
            Connect the output to a Report component
          </Button>
        </div>
      )}
      <Button
        type="primary"
        icon={<Icon component={() => MagicSvg({ style: { fill: '#FFF' } })} style={{ fontSize: 16 }} />}
        loading={generationLoading}
        style={{ marginTop: 8 }}
        onClick={() => generateWorkflow(inputValue)}
      >
        Generate
      </Button>
    </div>
  );
};

export default EditorGenerateInput;