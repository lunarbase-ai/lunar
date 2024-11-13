// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentDataType } from "@/models/component/ComponentModel"
import InputHandle from "../Handles/InputHandle"
import ParameterizedInput from "../ParameterizedInput/ParameterizedInput"
import FileInput from "../FileInput/FileInput"
import TextInput from "../TextInput/TextInput"
import CodeInput from "../CodeInput/CodeInput"
import PropertySelector from "../PropertySelector/PropertySelector"
import PropertyGetter from "../PropertyGetter/PropertyGetter"
import WorkflowInput from "../WorkflowInput/WorkflowInput"
import GraphQLInput from "../CodeInput/GraphQLInput"
import SQLInput from "../CodeInput/SQLInput"
import SPARQLInput from "../CodeInput/SPARQLInput"
import RCodeInput from "../CodeInput/RCodeInput"
import { useEffect } from "react"
import { getParameters } from "@/utils/helpers"
import ListInput from "../ListInput/ListInput"
import PasswordInput from "../PasswordInput/PasswordInput"

interface GenericInputProps {
  inputKey: string
  value: any
  inputType: ComponentDataType
  nodeId?: string
  onInputChange: (inputKey: string, inputValue: any) => void
  setParameters: (parameters: string[]) => void
}

const GenericInput: React.FC<GenericInputProps> = ({
  inputKey,
  value,
  inputType,
  nodeId,
  onInputChange,
  setParameters,
}) => {

  const stringValue = String(value ?? '')

  const handleChange = (key: string, value: string) => {
    setParameters(Array.from(new Set(getParameters(value ?? '').map(param => `${inputKey}.${param}`))))
    onInputChange(key, value)
  }

  useEffect(() => {
    setParameters(Array.from(new Set(getParameters(stringValue ?? '').map(param => `${inputKey}.${param}`))))
  }, [value])


  const renderByInputType = () => {
    if (
      inputType === ComponentDataType.JSON ||
      inputType === ComponentDataType.REPORT ||
      inputType === ComponentDataType.EMBEDDINGS ||
      inputType === ComponentDataType.AGGREGATED
    ) {
      return <InputHandle id={inputKey} />
    } else if (inputType === ComponentDataType.STREAM) {
      return <p>STREAM</p>
    } else if (inputType === ComponentDataType.TEMPLATE) {
      return <ParameterizedInput
        value={stringValue}
        onInputChange={(value) => handleChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.FILE) {
      return <FileInput
        value={value}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.TEXT) {
      return <TextInput
        value={value}
        onChange={value => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.CODE) {
      return <CodeInput
        value={stringValue}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.PROPERTY_SELECTOR && nodeId) {
      return <PropertySelector
        value={value}
        nodeId={nodeId}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.PROPERTY_GETTER && nodeId) {
      return <PropertyGetter
        value={value}
        name={inputKey}
        nodeId={nodeId}
        onInputChange={(inputKey, value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.WORKFLOW) {
      return <WorkflowInput
        value={value}
        onInputChange={value => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.GRAPHQL) {
      return <GraphQLInput
        value={stringValue}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.SQL) {
      return <SQLInput
        value={stringValue}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.SPARQL) {
      return <SPARQLInput
        value={stringValue}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.R_CODE) {
      return <RCodeInput
        value={stringValue}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.LIST) {
      return <ListInput
        value={value}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    } else if (inputType === ComponentDataType.PASSWORD) {
      return <PasswordInput
        value={value}
        onChange={value => onInputChange(inputKey, value)}
      />
    }
    else {
      return <ParameterizedInput
        value={value}
        onInputChange={(value) => onInputChange(inputKey, value)}
      />
    }
  }
  return <>
    {renderByInputType()}
  </>
}

export default GenericInput
