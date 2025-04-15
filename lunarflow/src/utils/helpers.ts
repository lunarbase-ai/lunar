// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Workflow } from "@/models/Workflow";
import { PARAMETER_REGEX } from "./regex"
import { FormInstance } from "antd";

const removeMaps = (input: string[]): string[] => {
  return input.map((str: string) => {
    const match = str.match(/^map\((\w+)\)$/);
    if (match) {
      return match[1];
    } else {
      return str;
    }
  });
};

export const getParameters = (value: string) => {
  const matches = value.match(PARAMETER_REGEX)
  if (matches != null) {
    const params = matches.map(match => match.replace(/[{}]/g, ''))
    return Array.from(new Set(removeMaps(params)))
  }
  return []
}

export const newSplit = (string: string, pattern: RegExp) => {
  const result: string[] = [];
  let lastIndex = 0;

  string.replace(pattern, (match, ...groups) => {
    const startIndex = string.indexOf(match, lastIndex);
    const endIndex = startIndex + match.length;

    result.push(string.slice(lastIndex, startIndex));
    result.push(string.slice(startIndex, endIndex));
    lastIndex = endIndex;

    return match;
  });

  result.push(string.slice(lastIndex));
  return result;
}

export const getAllEmptyVariables = (workflow: Workflow) => {
  const emptyVariables = new Set<string>()
  workflow.components.forEach(component => {
    let variables: Record<string, string> = {}
    component.inputs.forEach(input => {
      variables = { ...variables, ...input.templateVariables }
    })
    Object.keys(variables).forEach(variable => {
      if (variables[variable].length === 0) {
        emptyVariables.add(variable)
      }
    })
  })
  return Array.from(emptyVariables)
}

export const getVariables = (form: FormInstance<any>, workflow: Workflow) => {
  const result: Record<string, string> = {}
  if (workflow != null) {
    getAllEmptyVariables(workflow).forEach(variable => result[variable] = form.getFieldValue(variable))
  }
  return result
}
