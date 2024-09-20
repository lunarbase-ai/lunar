// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import api from "@/app/api/lunarverse";
import { AIModel } from "@/models/ai_model/AIModel";
import { Select, message } from "antd"
import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";

interface Props {
  value: string
  onChange: (value: string) => void;
}

const ModelSelector: React.FC<Props> = ({ value, onChange }) => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [options, setOptions] = useState<AIModel[]>()
  const [messageApi, contextHolder] = message.useMessage()
  const { data: session } = useSession()

  useEffect(() => {
    fetchModelConfiguration()
  }, [])

  const fetchModelConfiguration = () => {
    setIsLoading(true)
    if (session?.user?.email) {
      api.get<AIModel[]>(`/ai_model?user_id=${session?.user?.email}`)
        .then(({ data: modelTypes }) => {
          setOptions(modelTypes)
        })
        .catch((error) => {
          messageApi.error({
            content: error.message ?? `Failed to list model configuration. Details: ${error}`,
            onClick: () => messageApi.destroy()
          }, 0)
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      messageApi.error({
        content: 'Failed to list model configuration',
        onClick: () => messageApi.destroy()
      }, 0)
    }

  }

  const formattedOptions = options?.map(option => ({ value: option.key, label: option.label }))
  const formattedValue = options?.find(option => option.key === value)?.label ?? value

  return <>
    {contextHolder}
    <Select
      loading={isLoading}
      value={formattedValue}
      onChange={onChange}
      onClick={fetchModelConfiguration}
      style={{ width: '100%', marginBottom: 16 }}
      options={formattedOptions}
    />
  </>
}

export default ModelSelector
