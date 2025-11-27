'use client'

import './globals.css'
import { Inter } from 'next/font/google'
import { ReactNode, useState } from 'react'
import Sidebar from '@/components/Sidebar'
import TopBar from '@/components/TopBar'
import Toast from '@/components/Toast'
import { AppProvider, useApp } from '@/contexts/AppContext'
import { Toaster } from 'react-hot-toast'
import Head from 'next/head'

const inter = Inter({
    subsets: ['latin'],
    weight: ['300', '400', '500', '600', '700'],
    display: 'swap',
})

import { usePathname } from 'next/navigation'

function LayoutContent({ children }: { children: ReactNode }) {
    const pathname = usePathname()
    const isAuthPage = pathname === '/auth'

    const { showToast } = useApp()

    const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

    // Don't show sidebar/topbar on auth page
    if (isAuthPage) {
        return <div className="h-screen bg-white">{children}</div>
    }

    return (
        <div className="flex h-screen bg-white overflow-hidden">
            {/* Sidebar */}
            <Sidebar
                collapsed={sidebarCollapsed}
                onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <TopBar />

                {/* Main View Area */}
                <main className="flex-1 overflow-auto bg-white">
                    {children}
                </main>
            </div>

            {/* Toast Notification */}
            {showToast && <Toast message="New Tasks Assigned" />}
        </div>
    )
}

export default function RootLayout({ children }: { children: ReactNode }) {
    return (
        <html lang="en">
            <head>
                <title>Fission - AI-Powered Task Management</title>
                <meta name="description" content="AI-powered collaborative task management platform" />
                <link rel="icon" href="/fission-logo.jpg" />
            </head>
            <body className={inter.className}>
                <AppProvider>
                    <LayoutContent>{children}</LayoutContent>
                    <Toaster position="top-right" />
                    {/* Global Toast Container for WebSocket notifications */}
                    <ToastContainer />
                </AppProvider>
            </body>
        </html>
    )
}

// Import ToastContainer
import ToastContainer from '@/components/ToastContainer'
