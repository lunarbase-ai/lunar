// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { SessionProvider } from "next-auth/react"
import NewComponentForm from "../forms/NewComponentForm"

interface Props {
  id?: string
}

const NewComponent: React.FC<Props> = ({ id }) => {
  return <SessionProvider>
    <NewComponentForm id={id} />
  </SessionProvider>
}

export default NewComponent
