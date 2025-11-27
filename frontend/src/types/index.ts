// Backend types
export interface User {
    id: number
    email: string
    username: string
    is_active: boolean
    is_lead: boolean
    created_at: string
    updated_at: string
}

export interface TaskAssignment {
    user_id: number
    assigned_at: string
    user?: User
}

export interface BackendTask {
    id: number
    title: string
    description?: string
    status: 'todo' | 'in_progress' | 'done'
    priority: 'low' | 'medium' | 'high'
    created_by_id: number
    created_at: string
    updated_at: string
    room_id?: number
    assignments: TaskAssignment[]
}

export interface TaskStatistics {
    total: number
    todo: number
    in_progress: number
    done: number
    overdue: number
}

// Frontend types (legacy - for existing components)
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

export type SettingsTab = 'profile' | 'resume' | 'preferences' | 'notifications' | 'security'

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

// Room types
export type RoomRole = 'owner' | 'admin' | 'member'

export interface RoomMember {
    user_id: number
    role: RoomRole
    joined_at: string
    user?: User
}

export interface Room {
    id: number
    name: string
    description?: string
    created_by_id: number
    created_at: string
    updated_at: string
    members: RoomMember[]
}

// Notification types
export type NotificationType = 'task_assigned' | 'task_updated' | 'task_completed' | 'ai_analysis_completed' | 'system_alert';

export interface Notification {
    id: number;
    user_id: number;
    type: NotificationType;
    title: string;
    message: string;
    link_url?: string;
    payload?: any;
    is_read: boolean;
    created_at: string;
    read_at?: string;
}

// WebSocket message types
export interface WebSocketMessage {
    type: 'new_notification' | 'task_assigned' | 'ai_progress';
    data?: any;
    status?: string;
    message?: string;
}

// AI types with enhanced fields
export interface AISubtaskSuggestion {
    title: string;
    description: string;
    assigned_to_user_id: number | null;
    assigned_to_username: string | null;
    priority: 'low' | 'medium' | 'high' | 'urgent';
    estimated_time: string;
    estimated_hours?: number;
    due_date_days?: number;
    complexity_score?: number;
    required_skills: string[];
    reasoning: string;
}

export interface AIAnalysis {
    overall_strategy: string;
    subtasks: AISubtaskSuggestion[];
    warnings: string[];
}

// Alias for compatibility
export type SubtaskSuggestion = AISubtaskSuggestion;
export type TaskBreakdownResponse = AIAnalysis & {
    analysis_id: number;
    model_used: string;
    status: 'pending' | 'approved' | 'rejected';
};

export interface AnalysisHistoryItem {
    id: number;
    problem_description: string;
    created_at: string;
    status: string;
    subtask_count: number;
}
