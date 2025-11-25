export interface Task {
    id: number
    title: string
    tag: 'Frontend' | 'Backend' | 'UI'
    assignee: string
    complexity: 'Low' | 'Medium' | 'High'
    status: 'To Do' | 'In Progress' | 'Review' | 'Done'
}

export interface PipelineStep {
    id: number
    name: string
    duration: number
}

export type Role = 'teamlead' | 'employee'

export interface SidebarProps {
    collapsed: boolean
    onToggle: () => void
}

export interface TopBarProps {
    role: Role
    onRoleToggle: () => void
    hasNotification: boolean
    onNotificationClick: () => void
}

export interface TeamLeadViewProps {
    onAIComplete: () => void
}

export interface EmployeeViewProps {
    tasks: Task[]
}

export interface TaskCardProps {
    task: Task
}

export interface ToastProps {
    message: string
}

export interface AIAgentModalProps {
    onClose: () => void
    onComplete: () => void
}

export interface TeamMember {
    id: number
    name: string
    email: string
    role: string
    avatar: string
    status: 'online' | 'offline' | 'away'
    tasksAssigned: number
    tasksCompleted: number
}

export interface ActivityItem {
    id: number
    type: 'task_created' | 'task_completed' | 'member_added' | 'comment_added'
    title: string
    description: string
    timestamp: string
    user: string
}

export type SettingsTab = 'profile' | 'preferences' | 'notifications' | 'security'

export interface UserProfile {
    name: string
    email: string
    role: string
    avatar: string
    bio: string
}

export interface StatCardProps {
    title: string
    value: string | number
    icon: React.ReactNode
    trend?: {
        value: number
        isPositive: boolean
    }
}

export interface PageHeaderProps {
    title: string
    description: string
    action?: React.ReactNode
}
