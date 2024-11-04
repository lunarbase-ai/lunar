// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { ComponentModel } from "../component/ComponentModel";
import { Message } from "./message";

interface ChatResult {
  chat_id: null,
  chat_history: Message[],
  summary: string,
  cost: any,
  human_input: any[]
}

export interface ChatResponse {
  workflowOutput: Record<string, ComponentModel>
  chatResult: ChatResult
}
