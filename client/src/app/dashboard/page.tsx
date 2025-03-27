import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import DashboardClient from '@/components/dashboard/DashboardClient'

export default async function Dashboard() {
  
  // Server-side auth check
  const cookieStore = await cookies()
  const authToken = cookieStore.get('authToken')?.value

  

  if (!authToken) {
    redirect('/sign-in')
  }

  return <DashboardClient authToken={authToken} />
}