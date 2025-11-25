'use client'

import { useState } from 'react'
import PageHeader from '@/components/PageHeader'
import { Search, UserPlus, Mail, MoreVertical } from 'lucide-react'
import { TeamMember } from '@/types'

const mockTeamMembers: TeamMember[] = [
    {
        id: 1,
        name: 'John Doe',
        email: 'john.doe@company.com',
        role: 'Frontend Developer',
        avatar: 'JD',
        status: 'online',
        tasksAssigned: 8,
        tasksCompleted: 12,
    },
    {
        id: 2,
        name: 'Sarah Miller',
        email: 'sarah.miller@company.com',
        role: 'Backend Developer',
        avatar: 'SM',
        status: 'online',
        tasksAssigned: 6,
        tasksCompleted: 15,
    },
    {
        id: 3,
        name: 'Alex Kim',
        email: 'alex.kim@company.com',
        role: 'UI/UX Designer',
        avatar: 'AK',
        status: 'away',
        tasksAssigned: 4,
        tasksCompleted: 9,
    },
    {
        id: 4,
        name: 'Maria Garcia',
        email: 'maria.garcia@company.com',
        role: 'Product Manager',
        avatar: 'MG',
        status: 'offline',
        tasksAssigned: 10,
        tasksCompleted: 18,
    },
    {
        id: 5,
        name: 'David Chen',
        email: 'david.chen@company.com',
        role: 'DevOps Engineer',
        avatar: 'DC',
        status: 'online',
        tasksAssigned: 5,
        tasksCompleted: 11,
    },
    {
        id: 6,
        name: 'Emma Wilson',
        email: 'emma.wilson@company.com',
        role: 'QA Engineer',
        avatar: 'EW',
        status: 'away',
        tasksAssigned: 7,
        tasksCompleted: 14,
    },
]

export default function TeamsPage() {
    const [searchQuery, setSearchQuery] = useState('')

    const filteredMembers = mockTeamMembers.filter(member =>
        member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.role.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div className="p-8">
            <PageHeader
                title="Team"
                description="Manage your team members and view their performance"
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
                {filteredMembers.map((member) => (
                    <div
                        key={member.id}
                        className="bg-white border border-zinc-200 rounded-lg p-6 hover:shadow-md transition-all"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                {/* Avatar with Status */}
                                <div className="relative">
                                    <div className="w-12 h-12 rounded-full bg-black text-white flex items-center justify-center text-base font-medium">
                                        {member.avatar}
                                    </div>
                                    <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${member.status === 'online' ? 'bg-zinc-700' :
                                            member.status === 'away' ? 'bg-zinc-400' :
                                                'bg-zinc-300'
                                        }`} />
                                </div>

                                {/* Name & Role */}
                                <div>
                                    <h3 className="text-base font-semibold text-black">
                                        {member.name}
                                    </h3>
                                    <p className="text-xs text-zinc-500">{member.role}</p>
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
                            <span className="truncate">{member.email}</span>
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-zinc-100">
                            <div>
                                <div className="text-xl font-bold text-black">
                                    {member.tasksAssigned}
                                </div>
                                <div className="text-xs text-zinc-500">Assigned</div>
                            </div>
                            <div>
                                <div className="text-xl font-bold text-black">
                                    {member.tasksCompleted}
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
