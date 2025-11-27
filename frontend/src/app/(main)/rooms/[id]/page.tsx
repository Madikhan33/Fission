'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
    Users,
    Settings,
    Trash2,
    UserPlus,
    MoreVertical,
    Shield,
    ShieldAlert,
    User as UserIcon,
    Layout,
    Plus,
    Sparkles
} from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import AddMemberModal from '@/components/AddMemberModal'
import CreateTaskModal from '@/components/CreateTaskModal'
import KanbanBoard from '@/components/KanbanBoard'
import AIAssistantModal from '@/components/ai/AIAssistantModal'
import { roomsApi, authApi } from '@/services/api'
import { Room, RoomMember, User } from '@/types'

interface PageProps {
    params: {
        id: string
    }
}

export default function RoomDetailPage({ params }: PageProps) {
    const router = useRouter()
    const roomId = parseInt(params.id)

    const [room, setRoom] = useState<Room | null>(null)
    const [members, setMembers] = useState<RoomMember[]>([])
    const [currentUser, setCurrentUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false)
    const [isCreateTaskModalOpen, setIsCreateTaskModalOpen] = useState(false)
    const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false)
    const [taskStatus, setTaskStatus] = useState('todo')
    const [activeTab, setActiveTab] = useState<'tasks' | 'members'>('tasks')
    const [refreshTrigger, setRefreshTrigger] = useState(0)
    const [error, setError] = useState('')

    const fetchRoomData = async () => {
        try {
            const [roomData, membersData, userData] = await Promise.all([
                roomsApi.getById(roomId),
                roomsApi.getMembers(roomId),
                authApi.getMe()
            ])
            setRoom(roomData)
            setMembers(membersData)
            setCurrentUser(userData)
        } catch (err: any) {
            console.error('Failed to fetch room data:', err)
            setError('Failed to load room data')
            if (err.response?.status === 403 || err.response?.status === 404) {
                router.push('/rooms')
            }
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchRoomData()
    }, [roomId])

    const handleRemoveMember = async (userId: number) => {
        if (!confirm('Are you sure you want to remove this member?')) return

        try {
            await roomsApi.removeMember(roomId, userId)
            fetchRoomData()
        } catch (err) {
            console.error('Failed to remove member:', err)
            alert('Failed to remove member')
        }
    }

    const handleUpdateRole = async (userId: number, newRole: 'admin' | 'member') => {
        try {
            await roomsApi.updateMemberRole(roomId, userId, newRole)
            fetchRoomData()
        } catch (err) {
            console.error('Failed to update role:', err)
            alert('Failed to update role')
        }
    }

    const handleDeleteRoom = async () => {
        if (!confirm('Are you sure you want to delete this room? This action cannot be undone.')) return

        try {
            await roomsApi.delete(roomId)
            router.push('/rooms')
        } catch (err) {
            console.error('Failed to delete room:', err)
            alert('Failed to delete room')
        }
    }

    const handleCreateTask = (status: string = 'todo') => {
        setTaskStatus(status)
        setIsCreateTaskModalOpen(true)
    }

    if (isLoading) {
        return <div className="p-8 text-center">Loading...</div>
    }

    if (!room || !currentUser) return null

    const currentMember = members.find(m => m.user_id === currentUser.id)
    const isOwner = currentMember?.role === 'owner'
    const isAdmin = currentMember?.role === 'admin'
    const canManageMembers = isOwner || isAdmin

    return (
        <div className="space-y-6 h-full flex flex-col">
            <PageHeader
                title={room.name}
                description={room.description || 'No description'}
                action={
                    <div className="flex gap-2">
                        {isOwner && (
                            <button
                                onClick={() => setIsAIAssistantOpen(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors shadow-sm"
                            >
                                <Sparkles className="w-4 h-4" />
                                AI Assistant
                            </button>
                        )}
                        {activeTab === 'tasks' && (
                            <button
                                onClick={() => handleCreateTask()}
                                className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-zinc-800 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Create Task
                            </button>
                        )}
                        {activeTab === 'members' && canManageMembers && (
                            <button
                                onClick={() => setIsAddMemberModalOpen(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-zinc-800 transition-colors"
                            >
                                <UserPlus className="w-4 h-4" />
                                Add Member
                            </button>
                        )}
                        {isOwner && (
                            <button
                                onClick={handleDeleteRoom}
                                className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                                Delete Room
                            </button>
                        )}
                    </div>
                }
            />

            {/* Tabs */}
            <div className="flex border-b border-zinc-200">
                <button
                    onClick={() => setActiveTab('tasks')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'tasks'
                        ? 'border-black text-black'
                        : 'border-transparent text-zinc-500 hover:text-black'
                        }`}
                >
                    <Layout className="w-4 h-4" />
                    Tasks
                </button>
                <button
                    onClick={() => setActiveTab('members')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'members'
                        ? 'border-black text-black'
                        : 'border-transparent text-zinc-500 hover:text-black'
                        }`}
                >
                    <Users className="w-4 h-4" />
                    Members ({members.length})
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 min-h-0">
                {activeTab === 'tasks' ? (
                    <KanbanBoard
                        onCreateTask={handleCreateTask}
                        roomId={roomId}
                        refreshTrigger={refreshTrigger}
                    />
                ) : (
                    <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
                        <div className="divide-y divide-zinc-100">
                            {members.map((member) => (
                                <div key={member.user_id} className="p-4 flex items-center justify-between hover:bg-zinc-50 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-zinc-100 rounded-full flex items-center justify-center">
                                            <UserIcon className="w-5 h-5 text-zinc-500" />
                                        </div>
                                        <div>
                                            <div className="font-medium text-black flex items-center gap-2">
                                                {member.user?.username || `User ${member.user_id}`}
                                                {member.user_id === currentUser.id && (
                                                    <span className="text-xs bg-zinc-100 text-zinc-500 px-2 py-0.5 rounded-full">You</span>
                                                )}
                                            </div>
                                            <div className="text-sm text-zinc-500 flex items-center gap-1">
                                                {member.role === 'owner' && <ShieldAlert className="w-3 h-3 text-amber-500" />}
                                                {member.role === 'admin' && <Shield className="w-3 h-3 text-blue-500" />}
                                                <span className="capitalize">{member.role}</span>
                                                <span className="text-zinc-300">•</span>
                                                <span>Joined {new Date(member.joined_at).toLocaleDateString()}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {isOwner && member.role !== 'owner' && (
                                            <select
                                                value={member.role}
                                                onChange={(e) => handleUpdateRole(member.user_id, e.target.value as 'admin' | 'member')}
                                                className="text-sm border border-zinc-200 rounded px-2 py-1 focus:outline-none focus:border-black"
                                            >
                                                <option value="admin">Admin</option>
                                                <option value="member">Member</option>
                                            </select>
                                        )}

                                        {canManageMembers && member.role !== 'owner' && member.user_id !== currentUser.id && (
                                            <button
                                                onClick={() => handleRemoveMember(member.user_id)}
                                                className="p-2 text-zinc-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                                title="Remove member"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <AddMemberModal
                isOpen={isAddMemberModalOpen}
                onClose={() => setIsAddMemberModalOpen(false)}
                roomId={roomId}
                onMemberAdded={fetchRoomData}
            />

            <CreateTaskModal
                isOpen={isCreateTaskModalOpen}
                onClose={() => setIsCreateTaskModalOpen(false)}
                onTaskCreated={() => {
                    setRefreshTrigger(prev => prev + 1)
                }}
                defaultStatus={taskStatus as any}
                roomId={roomId}
            />

            <AIAssistantModal
                isOpen={isAIAssistantOpen}
                onClose={() => setIsAIAssistantOpen(false)}
                roomId={roomId}
                onTasksCreated={() => {
                    setRefreshTrigger(prev => prev + 1)
                }}
            />
        </div>
    )
}
