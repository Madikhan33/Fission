'use client'

import PageHeader from '@/components/PageHeader'
import StatCard from '@/components/StatCard'
import { CheckSquare, Clock, TrendingUp, Users, Activity } from 'lucide-react'
import { ActivityItem } from '@/types'

const mockActivities: ActivityItem[] = [
    {
        id: 1,
        type: 'task_completed',
        title: 'Task Completed',
        description: 'Design System Audit was completed by John Doe',
        timestamp: '2 hours ago',
        user: 'JD',
    },
    {
        id: 2,
        type: 'task_created',
        title: 'New Task Created',
        description: 'Refactor Auth Middleware was created by AI Agent',
        timestamp: '3 hours ago',
        user: 'AI',
    },
    {
        id: 3,
        type: 'member_added',
        title: 'Team Member Added',
        description: 'Sarah Miller joined the team',
        timestamp: '5 hours ago',
        user: 'SM',
    },
    {
        id: 4,
        type: 'comment_added',
        title: 'Comment Added',
        description: 'Alex Kim commented on API Integration',
        timestamp: '1 day ago',
        user: 'AK',
    },
]

export default function DashboardPage() {
    return (
        <div className="p-8">
            <PageHeader
                title="Dashboard"
                description="Overview of your tasks, team performance, and recent activity"
            />

            {/* Statistics Grid */}
            <div className="grid grid-cols-4 gap-6 mb-12">
                <StatCard
                    title="Total Tasks"
                    value={24}
                    icon={<CheckSquare className="w-5 h-5 text-black" />}
                    trend={{ value: 12, isPositive: true }}
                />
                <StatCard
                    title="In Progress"
                    value={8}
                    icon={<Clock className="w-5 h-5 text-black" />}
                />
                <StatCard
                    title="Completed"
                    value={14}
                    icon={<TrendingUp className="w-5 h-5 text-black" />}
                    trend={{ value: 8, isPositive: true }}
                />
                <StatCard
                    title="Team Members"
                    value={6}
                    icon={<Users className="w-5 h-5 text-black" />}
                />
            </div>

            {/* Recent Activity */}
            <div className="bg-white border border-zinc-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-6">
                    <Activity className="w-5 h-5 text-black" />
                    <h2 className="text-xl font-semibold text-black">Recent Activity</h2>
                </div>

                <div className="space-y-4">
                    {mockActivities.map((activity) => (
                        <div
                            key={activity.id}
                            className="flex items-start gap-4 p-4 rounded-lg hover:bg-zinc-50 transition-colors"
                        >
                            {/* User Avatar */}
                            <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center text-sm font-medium flex-shrink-0">
                                {activity.user}
                            </div>

                            {/* Activity Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <h3 className="text-sm font-semibold text-black mb-1">
                                            {activity.title}
                                        </h3>
                                        <p className="text-sm text-zinc-600">
                                            {activity.description}
                                        </p>
                                    </div>
                                    <span className="text-xs text-zinc-400 whitespace-nowrap">
                                        {activity.timestamp}
                                    </span>
                                </div>
                            </div>

                            {/* Activity Type Indicator */}
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-2 ${activity.type === 'task_completed' ? 'bg-zinc-700' :
                                    activity.type === 'task_created' ? 'bg-zinc-500' :
                                        activity.type === 'member_added' ? 'bg-zinc-400' :
                                            'bg-zinc-300'
                                }`} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-8 grid grid-cols-3 gap-6">
                <button className="bg-white border border-zinc-200 rounded-lg p-6 text-left hover:shadow-md transition-all group">
                    <div className="text-lg font-semibold text-black mb-2 group-hover:text-zinc-700">
                        Create New Task
                    </div>
                    <div className="text-sm text-zinc-600">
                        Add a new task to your workflow
                    </div>
                </button>

                <button className="bg-white border border-zinc-200 rounded-lg p-6 text-left hover:shadow-md transition-all group">
                    <div className="text-lg font-semibold text-black mb-2 group-hover:text-zinc-700">
                        Invite Team Member
                    </div>
                    <div className="text-sm text-zinc-600">
                        Add a new member to your team
                    </div>
                </button>

                <button className="bg-white border border-zinc-200 rounded-lg p-6 text-left hover:shadow-md transition-all group">
                    <div className="text-lg font-semibold text-black mb-2 group-hover:text-zinc-700">
                        View Reports
                    </div>
                    <div className="text-sm text-zinc-600">
                        Analyze team performance metrics
                    </div>
                </button>
            </div>
        </div>
    )
}
