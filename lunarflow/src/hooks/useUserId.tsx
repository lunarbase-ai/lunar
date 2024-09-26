// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"

export const useUserId = (): string | null => {
  const { data: session, status } = useSession()
  const { push } = useRouter()

  if (status === "unauthenticated") {
    push('/login')
  } else if (status === "loading") {
    return null
  }

  return session?.user?.email ?? null

}