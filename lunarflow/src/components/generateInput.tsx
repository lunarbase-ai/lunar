'use client'
import api from '@/app/api/lunarverse';
import { Workflow } from '@/models/Workflow';
import Icon from '@ant-design/icons';
import { Button, Input } from 'antd';
import { Session } from 'next-auth';
import React, { SVGProps, useState } from 'react'

const { Search } = Input

const MagicSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={16}
    height={16}
    fill="#3464DF"
    viewBox="0 0 24 24"
    {...props}
  >
    <path fill="none" d="M0 0h24v24H0z" />
    <path d="m19 9 1.25-2.75L23 5l-2.75-1.25L19 1l-1.25 2.75L15 5l2.75 1.25L19 9zm-7.5.5L9 4 6.5 9.5 1 12l5.5 2.5L9 20l2.5-5.5L17 12l-5.5-2.5zM19 15l-1.25 2.75L15 19l2.75 1.25L19 23l1.25-2.75L23 19l-2.75-1.25L19 15z" />
  </svg>
)

async function autoCreateWorkflow(name: string, description: string, session: Session) {
  if (session?.user?.email) {
    const { data } = await api.post<Workflow>(`/auto_workflow?user_id=${session.user.email}`,
      {
        workflow: {
          name: name,
          description: description,
          userId: session.user.email,
          auto_component_spacing: { dx: 450, dy: 350, x0: 0, y0: 0 }
        },
      })
    return data
  }
  throw new Error('Unauthenticated user!')
}

interface GenerateInputProps {
  session: Session
  redirectToWorkflowEditor: (workflowId: string) => void
}

const GenerateInput: React.FC<GenerateInputProps> = ({
  session,
  redirectToWorkflowEditor,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = () => {
    autoCreateWorkflowRequest('untitled', inputValue)
  };

  const autoCreateWorkflowRequest = (workflowName: string, workflowDescription: string) => {
    setIsLoading(true)
    autoCreateWorkflow(workflowName, workflowDescription, session)
      .then(({ id }) => {
        redirectToWorkflowEditor(id)
      })
      .catch((error) => {
        console.error(error)
        setIsLoading(false)
      })
  }

  return (
    <Search
      placeholder="Generate a Lunar workflow..."
      allowClear
      enterButton={<Button
        type='primary'
        icon={<Icon component={() => MagicSvg({ style: { fill: '#fff' } })} style={{ fontSize: 16 }} />}
        style={{ flexGrow: 1, background: 'linear-gradient(90deg, #4DB1DD 0%, #4DB1DD 24%, #69C3E2 100%)' }}
        className="generate-button"
        loading={isLoading}
      >
        Generate
      </Button>}
      size="large"
      onSearch={handleSubmit}
      onChange={handleInputChange}
      style={{
        maxWidth: 800,
        marginRight: 'auto',
        marginLeft: 'auto',
        marginTop: 32,
        marginBottom: 32,
      }}
    />
  );
};

export default GenerateInput;