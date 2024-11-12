import { getServerSession } from "next-auth"
import { redirect } from "next/navigation"

export const getUserId = async () => {
  const session = await getServerSession()
  if (!session?.user?.email) redirect('/login')
  return session.user.email
}
