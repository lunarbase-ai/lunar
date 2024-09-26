// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import React from 'react'
import * as polyQL from './regex'
import { newSplit } from '@/utils/helpers'
import CodeEditor from '@uiw/react-textarea-code-editor';
import rehypePrism from "rehype-prism-plus";
import rehypeRewrite from "rehype-rewrite";
import './style.css'
import './parameters.css'

const highlightRegex = /(?<!{){([\w\(\)]+)}(?!})/g

const splitValue = (value: string): string[] => {
  const splittedValue: string[] = []
  newSplit(value, highlightRegex).forEach(regexPart => {
    splittedValue.push(regexPart)
  })
  return splittedValue.filter(term => term != null) as string[]
}

interface ParameterizedInputProps {
  value: string
  onInputChange: (value: string) => void
}

const ParameterizedInput: React.FC<ParameterizedInputProps> = ({
  value,
  onInputChange,
}) => {

  return <div
    style={{
      maxHeight: 200,
      overflowY: 'scroll',
      border: '1px solid rgb(217, 217, 217)',
      borderRadius: 6,
    }}
  >
    <CodeEditor
      value={value}
      placeholder=""
      rehypePlugins={[
        [rehypePrism, { ignoreMissing: true }],
        [
          rehypeRewrite,
          {
            rewrite: (node: any, index: any, parent: any) => {
              if (node.type === "text" && !node.isFinal) {
                const nodesArray = splitValue(node.value)
                  .map((substring, i) => {
                    if (
                      substring.match(polyQL.PARAMETER_REGEX) !== null
                    ) {
                      return {
                        type: 'element',
                        tagName: 'span',
                        properties: {
                          className: ['parameter-highlight'],
                        },
                        children: [
                          {
                            type: 'text',
                            value: substring,
                            isFinal: true
                          },
                        ],
                      }
                    }
                    else {
                      return {
                        type: 'element',
                        tagName: 'span',
                        properties: {},
                        children: [
                          {
                            type: 'text',
                            value: substring,
                            isFinal: true
                          },
                        ],
                      }
                    }
                  })
                parent.children = nodesArray
              }
            }
          }
        ]
      ]}

      onChange={(event) => onInputChange(event.target.value)}
      padding={4}
      className="nodrag nowheel"
      style={{
        color: 'rgba(0, 0, 0, 0.88)',
        fontSize: 14,
        backgroundColor: "rgba(0, 0, 0, 0)",
        fontFamily: 'Source Code Pro, monospace',
      }}
    />
  </div>
}

export default ParameterizedInput
