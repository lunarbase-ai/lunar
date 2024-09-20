// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { OpenAI } from "openai";

const openai = new OpenAI({ apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY ?? '', dangerouslyAllowBrowser: true })

export const codeCompletion = async (code: string) => {
  const completion = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{
      role: 'user', content: `
      You are a code copilot.
When considering the given code, please note that it might contain comments starting with ## as instructions for you. Please follow these instructions to help the code work properly.
Simple comments that start with a single # are just normal comments. Output only the resulting code and the previously existing comments.
The code's output should be the content of the 'result' variable.
You cannot use external libraries.

      CODE: ${code}
      `}]
  })
  return completion.choices
}