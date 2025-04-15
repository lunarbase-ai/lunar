// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later
import NextAuth, { DefaultSession } from "next-auth"

declare module "next-auth" {

  interface Session {
    accessToken: string
    provider: string
  }

  interface JWT {
    accessToken: string
    provider: string
  }
}

declare module "*.svg" {
  const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
  export default content;
}
