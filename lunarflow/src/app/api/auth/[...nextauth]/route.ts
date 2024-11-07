// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import GithubProvider from "next-auth/providers/github"
import CredentialsProvider from "next-auth/providers/credentials"

const bypassAuthentication = process.env.BYPASS_AUTHENTICATION !== "false"
const providers = bypassAuthentication ? [
  CredentialsProvider({
    name: 'Enter your username',
    credentials: {
      username: { label: "Username", type: "text", placeholder: "Enter your username" },
    },
    async authorize(credentials, req) {
      return { id: "1", email: credentials?.username, name: credentials?.username }
    }
  }),
] : [
  GoogleProvider({
    clientId: process.env.GOOGLE_CLIENT_ID as string,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET as string
  }),
  GithubProvider({
    clientId: process.env.GITHUB_CLIENT_ID as string,
    clientSecret: process.env.GITHUB_CLIENT_SECRET as string
  })
]

const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET as string,
  providers: providers,
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }