// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client";

import { Button } from "antd";
import { useRouter } from "next/navigation";

interface Props {
  children?: React.ReactNode
  to: string
}

const RedirectButton: React.FC<Props> = ({ children, to }) => {
  const router = useRouter()
  return <Button
    type="link"
    style={{
      marginLeft: 'auto',
    }}
    onClick={() => router.push(to)}
  >
    {children}
  </Button>
}

export default RedirectButton;
