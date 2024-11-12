// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useSession } from "next-auth/react"

export const useUserId = (): string | null => {
  const { data: session, status } = useSession()

  if (status === "unauthenticated") {
    return null
  } else if (status === "loading") {
    return null
  }

  return session?.user?.email ?? null

}