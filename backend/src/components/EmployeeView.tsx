'use client'

import TaskCard from './TaskCard'
import { EmployeeViewProps } from '@/types'

interface Column {
    id: 'To Do' | 'In Progress' | 'Review' | 'Done'
    title: string
}

const columns: Column[] = [
    { id: 'To Do', title: 'To Do' },
    { id: 'In Progress', title: 'In Progress' },
    { id: 'Review', title: 'Review' },
    { id: 'Done', title: 'Done' },
]

export default function EmployeeView({ tasks }: EmployeeViewProps) {
    const getTasksByStatus = (status: Column['id']) => {
        return tasks.filter(task => task.status === status)
    }

    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-black mb-3">My Tasks</h1>
                <p className="text-zinc-500 text-lg">
                    Manage and track your assigned tasks across the workflow.
                </p>
            </div>

            {/* Kanban Board */}
            <div className="grid grid-cols-4 gap-6">
                {columns.map((column) => {
                    const columnTasks = getTasksByStatus(column.id)

                    return (
                        <div key={column.id} className="flex flex-col">
                            {/* Column Header */}
                            <div className="mb-4">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-sm font-semibold text-black uppercase tracking-wide">
                                        {column.title}
                                    </h2>
                                    <span className="text-xs text-zinc-400 font-medium bg-zinc-100 px-2 py-1 rounded">
                                        {columnTasks.length}
                                    </span>
                                </div>
                                <div className="h-0.5 bg-zinc-200 mt-3" />
                            </div>

                            {/* Task Cards */}
                            <div className="space-y-3 flex-1">
                                {columnTasks.length > 0 ? (
                                    columnTasks.map((task) => (
                                        <TaskCard key={task.id} task={task} />
                                    ))
                                ) : (
                                    <div className="border-2 border-dashed border-zinc-200 rounded-lg p-6 text-center">
                                        <p className="text-sm text-zinc-400">No tasks</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
