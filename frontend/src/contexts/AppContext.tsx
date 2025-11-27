'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { Role, Task, User } from '@/types'
import { authApi } from '@/services/api'
import { useWebSocket } from '@/hooks/useWebSocket'

interface AppContextType {
    user: User | null
    role: Role
    setRole: (role: Role) => void
    tasks: Task[]
    setTasks: (tasks: Task[]) => void
    hasNewNotification: boolean
    setHasNewNotification: (value: boolean) => void
    showToast: boolean
    setShowToast: (value: boolean) => void
    login: (token: string, user: User) => void
    logout: () => void
    isAuthenticated: boolean
    isLoading: boolean
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [role, setRole] = useState<Role>('employee')
    const [tasks, setTasks] = useState<Task[]>([])
    const [hasNewNotification, setHasNewNotification] = useState(false)
    const [showToast, setShowToast] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    // Initialize WebSocket
    const { reconnect, disconnect } = useWebSocket({
        onMessage: (msg) => {
            if (msg.type === 'task_assigned' && msg.data) {
                // Show toast for new task assignment
                if (window.showToast) {
                    window.showToast(
                        'New Task Assigned',
                        `You have been assigned to: ${msg.data.title}`,
                        'notification',
                        5000
                    )
                }
                setHasNewNotification(true)
            }

            if (msg.type === 'new_notification') {
                setHasNewNotification(true)
            }
        }
    })

    useEffect(() => {
        // Check for token on mount
        const token = localStorage.getItem('token')
        if (token) {
            authApi.getMe()
                .then(userData => {
                    setUser(userData)
                    setRole(userData.is_lead ? 'teamlead' : 'employee')
                    // WebSocket will auto-connect if token exists
                })
                .catch((error) => {
                    // IMPORTANT: Clear token if validation fails (401, etc.)
                    console.error('Token validation failed:', error)
                    localStorage.removeItem('token')
                    setUser(null)
                    setTasks([])
                    setHasNewNotification(false)
                    setShowToast(false)
                })
                .finally(() => {
                    setIsLoading(false)
                })
        } else {
            setIsLoading(false)
        }
    }, [])

    const login = (token: string, userData: User) => {
        // CRITICAL: Clear ALL previous state first to prevent cross-user data leakage
        setUser(null)
        setTasks([])
        setHasNewNotification(false)
        setShowToast(false)
        setRole('employee')

        // Clear localStorage to ensure no old data
        localStorage.removeItem('token')

        // Set new user data
        localStorage.setItem('token', token)
        setUser(userData)
        setRole(userData.is_lead ? 'teamlead' : 'employee')

        // Reconnect WebSocket with new token
        setTimeout(() => reconnect(), 100)
    }

    const logout = () => {
        authApi.logout().catch(() => { })
        localStorage.removeItem('token')
        setUser(null)
        setTasks([])
        setRole('employee') // Reset to default
        setHasNewNotification(false)
        setShowToast(false)

        // Disconnect WebSocket
        disconnect()

        // Force reload to clear any other component states
        window.location.href = '/auth'
    }

    return (
        <AppContext.Provider
            value={{
                user,
                role,
                setRole,
                tasks,
                setTasks,
                hasNewNotification,
                setHasNewNotification,
                showToast,
                setShowToast,
                login,
                logout,
                isAuthenticated: !!user,
                isLoading
            }}
        >
            {children}
        </AppContext.Provider>
    )
}

export function useApp() {
    const context = useContext(AppContext)
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider')
    }
    return context
}
