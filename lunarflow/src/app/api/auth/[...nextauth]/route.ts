// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import NextAuth from "next-auth"
import { authOptions } from "./authOptions"

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }