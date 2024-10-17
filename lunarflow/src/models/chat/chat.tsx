// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Message } from "./message";

export interface ChatResponse {
  chat_id: null,
  chat_history: Message[],
  summary: string,
  cost: any,
  human_input: any[]
}
