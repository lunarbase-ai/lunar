// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { useUserId } from "@/hooks/useUserId"
import { AutoComplete, Input } from "antd"
import { useRouter } from "next/navigation"
import { useState } from "react"
import debounce from 'lodash/debounce';
import { searchComponentsAction } from "@/app/actions/components"
import { ComponentModel } from "@/models/component/ComponentModel"

const ComponentSearch: React.FC = () => {

  const [options, setOptions] = useState<ComponentModel[]>([])
  const userId = useUserId()
  const router = useRouter()

  if (!userId) return <></>

  const handleSearch = (value: string) => {
    searchComponentsAction(value, userId)
      .then((result) => {
        setOptions(result)
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

export default ComponentSearch
