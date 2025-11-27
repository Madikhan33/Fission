'use client'

import { motion } from 'framer-motion'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import {
    LayoutDashboard,
    CheckSquare,
    Users,
    Settings,
    ChevronLeft,
    ChevronRight,
    Folder,
    LucideIcon
} from 'lucide-react'
import { SidebarProps } from '@/types'

interface NavItem {
    icon: LucideIcon
    label: string
    href: string
}

const navItems: NavItem[] = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: CheckSquare, label: 'My Tasks', href: '/tasks' },
    { icon: Users, label: 'Team', href: '/teams' },
    { icon: Folder, label: 'Rooms', href: '/rooms' },
    { icon: Settings, label: 'Settings', href: '/settings' },
]

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const pathname = usePathname()

    return (
        <motion.aside
            initial={false}
            animate={{ width: collapsed ? 64 : 240 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="bg-white border-r border-zinc-200 flex flex-col relative"
        >
            {/* Toggle Button */}
            <button
                onClick={onToggle}
                className="absolute -right-3 top-6 bg-white border border-zinc-200 rounded-full p-1 hover:bg-zinc-50 transition-colors z-10 shadow-sm"
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
                {collapsed ? (
                    <ChevronRight className="w-4 h-4 text-black" />
                ) : (
                    <ChevronLeft className="w-4 h-4 text-black" />
                )}
            </button>

            {/* Logo/Title */}
            <div className="h-16 flex items-center px-6 border-b border-zinc-200">
                {!collapsed && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex items-center gap-3"
                    >
                        <img
                            src="/fission-logo.jpg"
                            alt="Fission Logo"
                            className="w-8 h-8 rounded-full"
                        />
                        <h1 className="text-lg font-semibold text-black">Fission</h1>
                    </motion.div>
                )}
                {collapsed && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex justify-center"
                    >
                        <img
                            src="/fission-logo.jpg"
                            alt="Fission"
                            className="w-8 h-8 rounded-full"
                        />
                    </motion.div>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6">
                <ul className="space-y-1 px-3">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href

                        return (
                            <li key={item.label}>
                                <Link
                                    href={item.href}
                                    className={`flex items-center gap-3 px-3 py-2.5 rounded-md transition-all group ${isActive
                                        ? 'bg-black text-white'
                                        : 'text-zinc-700 hover:bg-zinc-100 hover:text-black'
                                        }`}
                                    title={collapsed ? item.label : undefined}
                                >
                                    <item.icon className="w-5 h-5 flex-shrink-0" />
                                    {!collapsed && (
                                        <motion.span
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            exit={{ opacity: 0 }}
                                            className="text-sm font-medium"
                                        >
                                            {item.label}
                                        </motion.span>
                                    )}
                                </Link>
                            </li>
                        )
                    })}
                </ul>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-zinc-200">
                {!collapsed && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="text-xs text-zinc-400 text-center"
                    >
                        v1.0.0
                    </motion.div>
                )}
            </div>
        </motion.aside>
    )
}
