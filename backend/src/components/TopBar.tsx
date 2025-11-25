'use client'

import { Bell } from 'lucide-react'
import { TopBarProps } from '@/types'

export default function TopBar({ role, onRoleToggle, hasNotification, onNotificationClick }: TopBarProps) {
    return (
        <header className="h-16 bg-white border-b border-zinc-200 flex items-center justify-between px-8">
            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 text-sm">
                <span className="text-zinc-400">Workspace</span>
                <span className="text-zinc-300">/</span>
                <span className="text-black font-medium">
                    {role === 'teamlead' ? 'Team Lead Dashboard' : 'My Tasks'}
                </span>
            </div>

            {/* Right Section: Role Switcher + Notification */}
            <div className="flex items-center gap-4">
                {/* Role Switcher Toggle */}
                <div className="flex items-center gap-3 bg-zinc-50 rounded-lg p-1 border border-zinc-200">
                    <button
                        onClick={onRoleToggle}
                        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${role === 'teamlead'
                                ? 'bg-black text-white'
                                : 'bg-transparent text-zinc-600 hover:text-black'
                            }`}
                    >
                        Team Lead
                    </button>
                    <button
                        onClick={onRoleToggle}
                        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${role === 'employee'
                                ? 'bg-black text-white'
                                : 'bg-transparent text-zinc-600 hover:text-black'
                            }`}
                    >
                        Employee
                    </button>
                </div>

                {/* Notification Bell */}
                <button
                    onClick={onNotificationClick}
                    className="relative p-2 hover:bg-zinc-100 rounded-lg transition-colors"
                    aria-label="Notifications"
                >
                    <Bell className="w-5 h-5 text-zinc-700" />
                    {hasNotification && (
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                    )}
                </button>
            </div>
        </header>
    )
}
