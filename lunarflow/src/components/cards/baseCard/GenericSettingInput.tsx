// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getDataSourcesAction } from "@/app/actions/dataSources";
import FetchSelect from "@/components/select/fetchSelect";
import { useUserId } from "@/hooks/useUserId";
import { FormInstance, Input, Switch } from "antd";

interface Props {
  settingKey: string
  form: FormInstance
}

const GenericSettingInput: React.FC<Props> = ({ settingKey, form }) => {

  const userId = useUserId()

  switch (settingKey) {
    case 'datasource':
      return userId ? <FetchSelect
        value={form.getFieldValue(settingKey)}
        onChange={(value) => {
          console.log(">>>VALUE", value.value)
          form.setFieldValue(
            settingKey,
            value.value
          )
        }}
        fetchOptions={async () => {
          const dataSources = await getDataSourcesAction(userId)
          return dataSources.map(dataSource => {
            return { label: dataSource.name, value: dataSource.id }
          })
        }} /> : <></>
    case 'force_run':
      return <Switch
        value={form.getFieldValue(settingKey)}
        onChange={(value) => form.setFieldValue(
          settingKey,
          value
        )}
      />
    default:
      return <Input
        value={form.getFieldValue(settingKey)}
        onChange={
          (event) => form.setFieldValue(
            settingKey,
            event.target.value
          )
        }
      />
  }
}

export default GenericSettingInput
