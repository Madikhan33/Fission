'use client'

import { createContext, useContext, useState, ReactNode } from 'react'
import { Role, Task } from '@/types'

interface AppContextType {
    role: Role
    setRole: (role: Role) => void
    tasks: Task[]
    setTasks: (tasks: Task[]) => void
    hasNewNotification: boolean
    setHasNewNotification: (value: boolean) => void
    showToast: boolean
    setShowToast: (value: boolean) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
    const [role, setRole] = useState<Role>('employee')
    const [tasks, setTasks] = useState<Task[]>([])
    const [hasNewNotification, setHasNewNotification] = useState(false)
    const [showToast, setShowToast] = useState(false)

    return (
        <AppContext.Provider
            value={{
                role,
                setRole,
                tasks,
                setTasks,
                hasNewNotification,
                setHasNewNotification,
                showToast,
                setShowToast,
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
