'use client'

import './globals.css'
import { Inter } from 'next/font/google'
import { ReactNode, useState } from 'react'
import Sidebar from '@/components/Sidebar'
import TopBar from '@/components/TopBar'
import Toast from '@/components/Toast'
import { AppProvider, useApp } from '@/contexts/AppContext'

const inter = Inter({
    subsets: ['latin'],
    weight: ['300', '400', '500', '600', '700'],
    display: 'swap',
})

function LayoutContent({ children }: { children: ReactNode }) {
    const {
        role,
        setRole,
        hasNewNotification,
        setHasNewNotification,
        showToast
    } = useApp()

    const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

    const toggleRole = () => {
        setRole(role === 'teamlead' ? 'employee' : 'teamlead')
    }

    const clearNotification = () => {
        setHasNewNotification(false)
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
                <TopBar
                    role={role}
                    onRoleToggle={toggleRole}
                    hasNotification={hasNewNotification}
                    onNotificationClick={clearNotification}
                />

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
            <body className={inter.className}>
                <AppProvider>
                    <LayoutContent>{children}</LayoutContent>
                </AppProvider>
            </body>
        </html>
    )
}
