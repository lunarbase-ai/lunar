// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { useUserId } from "@/hooks/useUserId"
import { AutoComplete, Input } from "antd"
import { SessionProvider } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import debounce from 'lodash/debounce';
import { searchWorkflowAction } from "@/app/actions/workflows"

interface Option {
  id: string
  name: string
}

const WorkflowSearchComponent: React.FC = () => {

  const [options, setOptions] = useState<Option[]>([])
  const userId = useUserId()
  const router = useRouter()

  //TODO: Show feedback
  if (!userId) return <></>

  const handleSearch = (value: string) => {
    searchWorkflowAction(value, userId)
      .then((result) => {
        setOptions(result)
      })
      .catch(error => {
        //TODO: Show feedback
        console.error(error)
      })
  }

  const onSelect = (value: string) => {
    console.log('onSelect', value);
  }

  return <AutoComplete
    style={{ width: '100%', marginTop: '40px' }}
    options={options?.map(option => {
      return {
        value: option.name,
        label: <div key={option.id} onClick={() => router.push(`/editor/${option.id}`)}>{option.name}</div>
      }
    })}
    onSelect={onSelect}
    onSearch={debounce(handleSearch, 300)}

  >
    <Input.Search size="large" placeholder="Search" enterButton />
  </AutoComplete>
}

const WorkflowSearch: React.FC = () => {
  return <SessionProvider>
    <WorkflowSearchComponent />
  </SessionProvider>
}

export default WorkflowSearch
