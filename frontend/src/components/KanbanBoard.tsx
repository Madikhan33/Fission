'use client'

import { useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { BackendTask } from '@/types'
import { tasksApi } from '@/services/api'
import { MoreHorizontal, Plus, Clock } from 'lucide-react'

const columns = {
    todo: { title: 'To Do', id: 'todo', color: 'bg-zinc-100' },
    in_progress: { title: 'In Progress', id: 'in_progress', color: 'bg-blue-50' },
    done: { title: 'Done', id: 'done', color: 'bg-green-50' }
}

interface KanbanBoardProps {
    onCreateTask?: (status: string) => void
    roomId?: number
    refreshTrigger?: number
    onlyMyTasks?: boolean
}

export default function KanbanBoard({ onCreateTask, roomId, refreshTrigger, onlyMyTasks }: KanbanBoardProps = {}) {
    const [tasks, setTasks] = useState<BackendTask[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        fetchTasks()
    }, [roomId, refreshTrigger, onlyMyTasks])

    const fetchTasks = async () => {
        try {
            const params: any = {}
            if (roomId) params.room_id = roomId

            let data
            if (onlyMyTasks) {
                data = await tasksApi.getMyTasks(params)
            } else {
                data = await tasksApi.getAll(params)
            }

            setTasks(data.tasks || [])
        } catch (error) {
            console.error('Failed to fetch tasks:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const onDragEnd = async (result: DropResult) => {
        const { destination, source, draggableId } = result

        // Если destination === null, значит перетащили за пределы droppable зон
        if (!destination) {
            const task = tasks.find(t => t.id.toString() === draggableId)
            if (!task) return

            if (confirm(`Are you sure you want to delete task "${task.title}"?`)) {
                // Optimistic update
                const updatedTasks = tasks.filter(t => t.id.toString() !== draggableId)
                setTasks(updatedTasks)

                try {
                    await tasksApi.delete(task.id)
                } catch (error) {
                    console.error('Failed to delete task:', error)
                    // Revert on error
                    fetchTasks()
                }
            }
            return
        }

        if (
            destination.droppableId === source.droppableId &&
            destination.index === source.index
        ) {
            return
        }

        const task = tasks.find(t => t.id.toString() === draggableId)
        if (!task) return

        // Optimistic update
        const newStatus = destination.droppableId as BackendTask['status']
        const updatedTasks = tasks.map(t =>
            t.id.toString() === draggableId ? { ...t, status: newStatus } : t
        )
        setTasks(updatedTasks)

        try {
            await tasksApi.updateStatus(task.id, newStatus)
        } catch (error) {
            console.error('Failed to update task status:', error)
            // Revert on error
            fetchTasks()
        }
    }

    const getTasksByStatus = (status: string) => {
        return tasks.filter(task => task.status === status)
    }

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'bg-red-100 text-red-700'
            case 'medium': return 'bg-yellow-100 text-yellow-700'
            case 'low': return 'bg-green-100 text-green-700'
            default: return 'bg-zinc-100 text-zinc-700'
        }
    }

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-zinc-500">Loading tasks...</div>
            </div>
        )
    }

    return (
        <div className="h-full overflow-x-auto">
            <DragDropContext onDragEnd={onDragEnd}>
                <div className="flex gap-6 h-full min-w-[1000px] p-6">
                    {Object.values(columns).map((column) => (
                        <div key={column.id} className="flex-1 min-w-[300px] flex flex-col bg-zinc-50 rounded-xl border border-zinc-200">
                            {/* Column Header */}
                            <div className="p-4 flex items-center justify-between border-b border-zinc-200">
                                <div className="flex items-center gap-2">
                                    <h3 className="font-semibold text-zinc-900">{column.title}</h3>
                                    <span className="bg-zinc-200 text-zinc-600 px-2 py-0.5 rounded-full text-xs font-medium">
                                        {getTasksByStatus(column.id).length}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <button
                                        onClick={() => onCreateTask?.(column.id)}
                                        className="p-1 hover:bg-zinc-200 rounded text-zinc-500"
                                        title="Add task"
                                    >
                                        <Plus className="w-4 h-4" />
                                    </button>
                                    <button className="p-1 hover:bg-zinc-200 rounded text-zinc-500">
                                        <MoreHorizontal className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {/* Tasks List */}
                            <Droppable droppableId={column.id}>
                                {(provided, snapshot) => (
                                    <div
                                        ref={provided.innerRef}
                                        {...provided.droppableProps}
                                        className={`flex-1 p-3 space-y-3 overflow-y-auto transition-colors ${snapshot.isDraggingOver ? 'bg-zinc-100/50' : ''
                                            }`}
                                    >
                                        {getTasksByStatus(column.id).map((task, index) => (
                                            <Draggable
                                                key={task.id}
                                                draggableId={task.id.toString()}
                                                index={index}
                                            >
                                                {(provided, snapshot) => (
                                                    <div
                                                        ref={provided.innerRef}
                                                        {...provided.draggableProps}
                                                        {...provided.dragHandleProps}
                                                        className={`bg-white p-4 rounded-lg border border-zinc-200 shadow-sm hover:shadow-md transition-shadow group cursor-grab active:cursor-grabbing ${snapshot.isDragging ? 'shadow-lg ring-2 ring-black rotate-1' : ''
                                                            }`}
                                                    >
                                                        <div className="flex items-start justify-between mb-2">
                                                            <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
                                                                {task.priority}
                                                            </span>
                                                            <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-zinc-100 rounded text-zinc-400">
                                                                <MoreHorizontal className="w-4 h-4" />
                                                            </button>
                                                        </div>
                                                        <h4 className="font-medium text-zinc-900 mb-1">{task.title}</h4>
                                                        {task.description && (
                                                            <p className="text-sm text-zinc-500 line-clamp-2 mb-3">
                                                                {task.description}
                                                            </p>
                                                        )}
                                                        <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-100">
                                                            <div className="flex items-center gap-1 text-xs text-zinc-400">
                                                                <Clock className="w-3 h-3" />
                                                                {new Date(task.created_at).toLocaleDateString()}
                                                            </div>

                                                            {/* Assignees Display */}
                                                            {task.assignments && task.assignments.length > 0 ? (
                                                                task.assignments.length === 1 ? (
                                                                    <div className="flex items-center gap-2 bg-zinc-50 px-2 py-1 rounded-full border border-zinc-100">
                                                                        <div className="w-5 h-5 rounded-full bg-black text-white flex items-center justify-center text-[10px] font-medium">
                                                                            {task.assignments[0].user?.username?.[0]?.toUpperCase()}
                                                                        </div>
                                                                        <span className="text-xs font-medium text-zinc-700 max-w-[80px] truncate">
                                                                            {task.assignments[0].user?.username}
                                                                        </span>
                                                                    </div>
                                                                ) : (
                                                                    <div className="flex -space-x-2">
                                                                        {task.assignments.slice(0, 3).map((assignment) => (
                                                                            <div
                                                                                key={assignment.user_id}
                                                                                className="w-6 h-6 rounded-full bg-zinc-800 border-2 border-white flex items-center justify-center text-[10px] text-white font-medium"
                                                                                title={assignment.user?.username}
                                                                            >
                                                                                {assignment.user?.username?.[0]?.toUpperCase()}
                                                                            </div>
                                                                        ))}
                                                                        {task.assignments.length > 3 && (
                                                                            <div className="w-6 h-6 rounded-full bg-zinc-400 border-2 border-white flex items-center justify-center text-[10px] text-white font-medium">
                                                                                +{task.assignments.length - 3}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                )
                                                            ) : (
                                                                <div className="text-xs text-zinc-400 italic">
                                                                    Unassigned
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}
                                            </Draggable>
                                        ))}
                                        {provided.placeholder}
                                    </div>
                                )}
                            </Droppable>
                        </div>
                    ))}
                </div>
            </DragDropContext>
        </div>
    )
}
