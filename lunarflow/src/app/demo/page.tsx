// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '../api/auth/[...nextauth]/authOptions';
import api from '../api/lunarverse';


export default async function Root() {
  const session = await getServerSession(authOptions)

  if (session?.user?.email == null) {
    redirect('/login')
  } else {
    api.post('/login?user_id=' + session.user.email)
    redirect('/demo/home')
  }
}
