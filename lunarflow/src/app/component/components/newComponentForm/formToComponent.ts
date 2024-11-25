// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentInput } from "@/models/component/ComponentInput"
import { ComponentDataType, ComponentModel } from "@/models/component/ComponentModel"

export const getFormValues = (component: ComponentModel) => {
  const inputs = component?.inputs.map(input => ({ input_name: input.key, input_type: input.dataType }))
  const currentConfiguration = component?.configuration
  const configuration = component ? Object.keys(currentConfiguration).map(conf => ({ name: conf, value: currentConfiguration[conf] })) : []
  return {
    component_name: component?.name,
    component_description: component?.description,
    component_group: component?.group,
    input_types: inputs,
    output_type: component?.output.dataType,
    configuration: configuration,
    code: component?.componentCode,
    code_dependencies: component?.componentCodeRequirements || []
  }
}

//TODO: remove code (it should be passed in values)
//TODO: Type values
export const getComponentFromValues = (
  values: any,
  code: string,
  id?: string,
) => {
  const inputTypes: { input_name: string, input_type: string, input_value?: string }[] | undefined = values["input_types"]
  const newInputs = inputTypes?.map(input => {
    const newInput: ComponentInput = {
      key: input.input_name,
      value: input.input_value,
      dataType: ComponentDataType[input.input_type as keyof typeof ComponentDataType],
      templateVariables: {},
      componentId: id ?? null,
    }
    return newInput
  })
  const newConfig: Record<string, string> = {}
  const configuration: { name: string, value: string }[] | undefined = values["configuration"]
  configuration?.forEach(config => {
    newConfig[config.name] = config.value
  })
  const newComponentModel: ComponentModel = {
    id: id,
    name: values["component_name"],
    className: "Custom",
    description: values["component_description"],
    group: values["component_group"],
    inputs: newInputs || [],
    output: {
      key: "",
      value: undefined,
      dataType: values["output_type"]
    },
    configuration: newConfig,
    isCustom: true,
    isTerminal: false,
    componentCode: code,
    componentCodeRequirements: values["code_dependencies"],
    invalidErrors: [],
  }
  return newComponentModel
}
