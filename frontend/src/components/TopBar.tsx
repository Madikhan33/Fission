'use client'

import { LogOut } from 'lucide-react'
import { useApp } from '@/contexts/AppContext'
import NotificationBell from './NotificationBell'

export default function TopBar() {
    const { user, logout } = useApp()

    return (
        <header className="h-16 bg-white border-b border-zinc-200 flex items-center justify-between px-8">
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm">
                <span className="text-zinc-400">Workspace</span>
                <span className="text-zinc-300">/</span>
                <span className="text-black font-medium">
                    {user?.is_lead ? 'Team Lead Dashboard' : 'My Tasks'}
                </span>
            </div>

            {/* Right Section: User Info */}
            <div className="flex items-center gap-4">
                {/* Notification Bell */}
                <NotificationBell />

                {/* User Info */}
                {user && (
                    <div className="flex items-center gap-3 pl-3 border-l border-zinc-200">
                        <div className="text-right">
                            <div className="text-sm font-medium text-black">{user.username}</div>
                            <div className="text-xs text-zinc-500">{user.is_lead ? 'Team Lead' : 'Employee'}</div>
                        </div>
                        <button
                            onClick={logout}
                            className="p-2 hover:bg-zinc-100 rounded-lg transition-colors"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5 text-zinc-700" />
                        </button>
                    </div>
                )}
            </div>
        </header>
    )
}
