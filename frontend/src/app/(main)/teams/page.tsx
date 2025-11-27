'use client'

import { useState, useEffect } from 'react'
import PageHeader from '@/components/PageHeader'
import { Search, UserPlus, Mail, MoreVertical } from 'lucide-react'
import { authApi } from '@/services/api'
import { User } from '@/types'

export default function TeamsPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [users, setUsers] = useState<User[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                // FIXED: Use getTeamMembers to get only users from same rooms
                const data = await authApi.getTeamMembers()
                setUsers(data)
            } catch (error) {
                console.error('Failed to fetch team members:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchUsers()
    }, [])

    const filteredMembers = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
    )

    if (loading) {
        return <div className="p-8 text-center text-zinc-500">Loading team members...</div>
    }

    return (
        <div className="p-8">
            <PageHeader
                title="Team"
                description="Manage your team members"
                action={
                    <button className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-zinc-800 transition-colors flex items-center gap-2">
                        <UserPlus className="w-4 h-4" />
                        Add Member
                    </button>
                }
            />

            {/* Search Bar */}
            <div className="mb-8">
                <div className="relative max-w-md">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                    <input
                        type="text"
                        placeholder="Search team members..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>
            </div>

            {/* Team Members Grid */}
            <div className="grid grid-cols-3 gap-6">
                {filteredMembers.map((user) => (
                    <div
                        key={user.id}
                        className="bg-white border border-zinc-200 rounded-lg p-6 hover:shadow-md transition-all"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                {/* Avatar with Status */}
                                <div className="relative">
                                    <div className="w-12 h-12 rounded-full bg-black text-white flex items-center justify-center text-base font-medium uppercase">
                                        {user.username.substring(0, 2)}
                                    </div>
                                    <div className="absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white bg-zinc-300" title="Offline" />
                                </div>

                                {/* Name & Role */}
                                <div>
                                    <h3 className="text-base font-semibold text-black">
                                        {user.username}
                                    </h3>
                                    <p className="text-xs text-zinc-500">
                                        {user.is_lead ? 'Team Lead' : 'Employee'}
                                    </p>
                                </div>
                            </div>

                            {/* More Options */}
                            <button className="p-1 hover:bg-zinc-100 rounded transition-colors">
                                <MoreVertical className="w-4 h-4 text-zinc-400" />
                            </button>
                        </div>

                        {/* Email */}
                        <div className="flex items-center gap-2 mb-4 text-sm text-zinc-600">
                            <Mail className="w-4 h-4" />
                            <span className="truncate">{user.email}</span>
                        </div>

                        {/* Stats Placeholder */}
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-zinc-100">
                            <div>
                                <div className="text-xl font-bold text-black">
                                    -
                                </div>
                                <div className="text-xs text-zinc-500">Assigned</div>
                            </div>
                            <div>
                                <div className="text-xl font-bold text-black">
                                    -
                                </div>
                                <div className="text-xs text-zinc-500">Completed</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {filteredMembers.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-zinc-400">No team members found</p>
                </div>
            )}
        </div>
    )
}
