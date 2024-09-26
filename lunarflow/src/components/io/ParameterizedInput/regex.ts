// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export const CONCATENATION_REGEX = /((?<!{){([\w\(\)]+)}(?!})|SELECT|FROM|LIMIT|\{|\}|\.|;|,|\||~|:|==|!=|>=|>|<=|<|[-+]?\d+(?:\.\d+)?|\?[a-zA-Z_][a-zA-Z0-9_]*)/g

export const SELECT_REGEX = /(SELECT)/g

export const FROM_REGEX = /(FROM)/g

export const LIMIT_REGEX = /(LIMIT)/g

export const LEFT_BRACK_REGEX = /(\{)/g

export const RIGHT_BRACK_REGEX = /(\})/g

export const DOT_REGEX = /(\.)/g

export const SEMICOLON_REGEX = /(;)/g

export const COMMA_REGEX = /(,)/g

export const BAR_REGEX = /(\|)/g

export const NEURAL_REGEX = /(~)/g

export const EXACT_REGEX = /(:)/g

export const EQUALITY_REGEX = /(==)/g

export const INEQUALITY_REGEX = /(!=)/g

export const GEQ_REGEX = /(>=)/g

export const GREATER_REGEX = /(>)/g

export const LEQ_REGEX = /(<=)/g

export const LESS_REGEX = /(<)/g

export const NUMBER_REGEX = /([-+]?\d+(?:\.\d+)?)/g

export const VARIABLE_REGEX = /(\?[a-zA-Z_][a-zA-Z0-9_]*)/g

export const STRING_REGEX = /("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')/g

export const IDENTIFIER_REGEX = /([a-zA-Z_][a-zA-Z0-9_]*)/g

export const PARAMETER_REGEX = /(?<!{){([\w\(\)]+)}(?!})/g
