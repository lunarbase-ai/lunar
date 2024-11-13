// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"

export const useUserId = (): string | null => {
  const { data: session, status } = useSession()
  const [userId, setUserId] = useState<string | null>(null)

  useEffect(() => {
    if (status === "unauthenticated" || status === "loading") {
      setUserId(null)
    } else {
      setUserId(session?.user?.email ?? null)
    }
  }, [status, session])

  return userId
}