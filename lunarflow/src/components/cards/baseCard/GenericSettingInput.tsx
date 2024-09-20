// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import ModelSelector from "@/components/io/ModelSelector/ModelSelector";
import { FormInstance, Input, Switch } from "antd";

interface Props {
  settingKey: string
  form: FormInstance
}

const GenericSettingInput: React.FC<Props> = ({ settingKey, form }) => {
  switch (settingKey) {
    case 'ai_model_config':
      return <ModelSelector
        value={form.getFieldValue(settingKey)}
        onChange={(value) => form.setFieldValue(settingKey, value)}
      />
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
