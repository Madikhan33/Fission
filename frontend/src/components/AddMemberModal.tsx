'use client'

import { useState, useEffect } from 'react'
import { X, Search, User as UserIcon } from 'lucide-react'
import { roomsApi, authApi } from '@/services/api'
import { User } from '@/types'

interface AddMemberModalProps {
    isOpen: boolean
    onClose: () => void
    roomId: number
    onMemberAdded: () => void
}

export default function AddMemberModal({ isOpen, onClose, roomId, onMemberAdded }: AddMemberModalProps) {
    const [users, setUsers] = useState<User[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
    const [role, setRole] = useState<'admin' | 'member'>('member')
    const [isLoading, setIsLoading] = useState(false)
    const [isFetchingUsers, setIsFetchingUsers] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (isOpen) {
            fetchUsers()
        }
    }, [isOpen])

    const fetchUsers = async () => {
        setIsFetchingUsers(true)
        try {
            const data = await authApi.getAllUsers()
            setUsers(data)
        } catch (err) {
            console.error('Failed to fetch users:', err)
        } finally {
            setIsFetchingUsers(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedUserId) return

        setError('')
        setIsLoading(true)

        try {
            await roomsApi.addMember(roomId, {
                user_id: selectedUserId,
                role
            })

            // Reset form
            setSelectedUserId(null)
            setRole('member')
            setSearchQuery('')

            onMemberAdded()
            onClose()
        } catch (err: any) {
            console.error('Add member error:', err)
            setError(err.response?.data?.detail || 'Failed to add member')
        } finally {
            setIsLoading(false)
        }
    }

    const filteredUsers = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
    )

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-zinc-200">
                    <h2 className="text-xl font-semibold text-black">Add Member</h2>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-zinc-100 rounded transition-colors"
                    >
                        <X className="w-5 h-5 text-zinc-500" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Search User */}
                    <div>
                        <label className="block text-sm font-medium text-black mb-2">
                            Select User
                        </label>
                        <div className="relative mb-2">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search by name or email"
                                className="w-full pl-9 pr-4 py-2 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                            />
                        </div>

                        <div className="max-h-48 overflow-y-auto border border-zinc-200 rounded-lg divide-y divide-zinc-100">
                            {isFetchingUsers ? (
                                <div className="p-4 text-center text-sm text-zinc-500">Loading users...</div>
                            ) : filteredUsers.length === 0 ? (
                                <div className="p-4 text-center text-sm text-zinc-500">No users found</div>
                            ) : (
                                filteredUsers.map(user => (
                                    <div
                                        key={user.id}
                                        onClick={() => setSelectedUserId(user.id)}
                                        className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-zinc-50 transition-colors ${selectedUserId === user.id ? 'bg-zinc-100' : ''
                                            }`}
                                    >
                                        <div className="w-8 h-8 bg-zinc-200 rounded-full flex items-center justify-center">
                                            <UserIcon className="w-4 h-4 text-zinc-500" />
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-black">{user.username}</div>
                                            <div className="text-xs text-zinc-500">{user.email}</div>
                                        </div>
                                        {selectedUserId === user.id && (
                                            <div className="ml-auto w-2 h-2 bg-black rounded-full" />
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Role */}
                    <div>
                        <label htmlFor="role" className="block text-sm font-medium text-black mb-2">
                            Role
                        </label>
                        <select
                            id="role"
                            value={role}
                            onChange={(e) => setRole(e.target.value as 'admin' | 'member')}
                            className="w-full px-4 py-2 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                        >
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-zinc-200 rounded-lg text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || !selectedUserId}
                            className="flex-1 px-4 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Adding...' : 'Add Member'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
