'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useApp } from '@/contexts/AppContext'

export default function Home() {
    const { isAuthenticated, isLoading } = useApp()
    const router = useRouter()

    useEffect(() => {
        if (!isLoading) {
            if (isAuthenticated) {
                router.push('/dashboard')
            } else {
                router.push('/auth')
            }
        }
    }, [isAuthenticated, isLoading, router])

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-zinc-500">Loading...</div>
            </div>
        )
    }

    return null
}
