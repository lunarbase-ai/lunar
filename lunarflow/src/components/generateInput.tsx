'use client'
import { autoCreateWorkflowAction } from '@/app/actions/copilot';
import { useUserId } from '@/hooks/useUserId';
import Icon from '@ant-design/icons';
import { Button, Input } from 'antd';
import { useRouter } from 'next/navigation';
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

interface GenerateInputProps { }

const GenerateInput: React.FC<GenerateInputProps> = ({ }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter()

  const userId = useUserId()

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = () => {
    autoCreateWorkflowRequest('untitled', inputValue)
  };

  const autoCreateWorkflowRequest = (workflowName: string, workflowDescription: string) => {
    setIsLoading(true)
    if (userId) {
      autoCreateWorkflowAction(workflowName, workflowDescription, userId)
        .then(({ id }) => {
          router.push(`/editor/${id}`)
        })
        .catch((error) => {
          console.error(error)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
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