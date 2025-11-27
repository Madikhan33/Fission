'use client'

import { useState, useEffect } from 'react'
import PageHeader from '@/components/PageHeader'
import StatCard from '@/components/StatCard'
import { CheckSquare, Clock, TrendingUp, Users, Activity, AlertTriangle } from 'lucide-react'
import { tasksApi } from '@/services/api'
import { TaskStatistics, BackendTask } from '@/types'

export default function DashboardPage() {
    const [stats, setStats] = useState<TaskStatistics | null>(null)
    const [recentTasks, setRecentTasks] = useState<BackendTask[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch stats
                const statsData = await tasksApi.getMyStats()
                setStats(statsData)

                // Fetch recent tasks as activity log
                const tasksData = await tasksApi.getMyTasks({ page: 1, page_size: 5 })
                setRecentTasks(tasksData.tasks || [])
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    if (loading) {
        return <div className="p-8 text-center text-zinc-500">Loading dashboard...</div>
    }

    return (
        <div className="p-8">
            <PageHeader
                title="Dashboard"
                description="Overview of your tasks and recent activity"
            />

            {/* Statistics Grid */}
            <div className="grid grid-cols-4 gap-6 mb-12">
                <StatCard
                    title="Total Tasks"
                    value={stats?.total || 0}
                    icon={<CheckSquare className="w-5 h-5 text-black" />}
                />
                <StatCard
                    title="In Progress"
                    value={stats?.in_progress || 0}
                    icon={<Clock className="w-5 h-5 text-black" />}
                />
                <StatCard
                    title="Completed"
                    value={stats?.done || 0}
                    icon={<TrendingUp className="w-5 h-5 text-black" />}
                />
                <StatCard
                    title="Overdue"
                    value={stats?.overdue || 0}
                    icon={<AlertTriangle className="w-5 h-5 text-red-500" />}
                />
            </div>

            {/* Recent Activity (Tasks) */}
            <div className="bg-white border border-zinc-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-6">
                    <Activity className="w-5 h-5 text-black" />
                    <h2 className="text-xl font-semibold text-black">Recent Tasks</h2>
                </div>

                <div className="space-y-4">
                    {recentTasks.length > 0 ? (
                        recentTasks.map((task) => (
                            <div
                                key={task.id}
                                className="flex items-start gap-4 p-4 rounded-lg hover:bg-zinc-50 transition-colors border border-zinc-100"
                            >
                                {/* Status Indicator */}
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 ${task.status === 'done' ? 'bg-green-100 text-green-700' :
                                        task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                                            'bg-zinc-100 text-zinc-700'
                                    }`}>
                                    {task.status === 'done' ? '✓' :
                                        task.status === 'in_progress' ? '↻' : '○'}
                                </div>

                                {/* Task Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <h3 className="text-sm font-semibold text-black mb-1">
                                                {task.title}
                                            </h3>
                                            <p className="text-sm text-zinc-600 line-clamp-1">
                                                {task.description || 'No description'}
                                            </p>
                                        </div>
                                        <span className="text-xs text-zinc-400 whitespace-nowrap">
                                            {new Date(task.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="mt-2 flex items-center gap-2">
                                        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${task.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                                                task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-green-100 text-green-700'
                                            }`}>
                                            {task.priority}
                                        </span>
                                        {task.room_id && (
                                            <span className="text-xs text-zinc-400">
                                                Room #{task.room_id}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-8 text-zinc-500">
                            No recent tasks found
                        </div>
                    )}
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
                        View My Tasks
                    </div>
                    <div className="text-sm text-zinc-600">
                        See all tasks assigned to you
                    </div>
                </button>

                <button className="bg-white border border-zinc-200 rounded-lg p-6 text-left hover:shadow-md transition-all group">
                    <div className="text-lg font-semibold text-black mb-2 group-hover:text-zinc-700">
                        View Reports
                    </div>
                    <div className="text-sm text-zinc-600">
                        Analyze performance metrics
                    </div>
                </button>
            </div>
        </div>
    )
}
