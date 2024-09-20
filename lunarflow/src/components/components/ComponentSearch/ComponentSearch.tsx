// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import api from "@/app/api/lunarverse"
import { useUserId } from "@/hooks/useUserId"
import { AutoComplete, Input } from "antd"
import { SessionProvider } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import debounce from 'lodash/debounce';

interface Option {
  id: string
  name: string
}

const ComponentSearchComponent: React.FC = () => {

  const [options, setOptions] = useState<Option[]>([])
  const userId = useUserId()
  const router = useRouter()


  const handleSearch = (value: string) => {
    api.get<Option[]>(`/component/search?query=${value}&user_id=${userId}`)
      .then(({ data }) => {
        setOptions(data)
      })
      .catch(error => console.error(error))
  }

  const onSelect = (value: string) => {
    console.log('onSelect', value);
  }

  return <AutoComplete
    style={{ width: '100%', marginTop: '40px' }}
    options={options?.map(option => {
      return {
        value: option.name,
        label: <div key={option.id} onClick={() => router.push(`/component/${option.id}`)}>{option.name}</div>
      }
    })}
    onSelect={onSelect}
    onSearch={debounce(handleSearch, 300)}

  >
    <Input.Search size="large" placeholder="Search" enterButton />
  </AutoComplete>
}

const ComponentSearch: React.FC = () => {
  return <SessionProvider>
    <ComponentSearchComponent />
  </SessionProvider>
}

export default ComponentSearch
