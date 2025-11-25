'use client'

import { useEffect } from 'react'
import TeamLeadView from '@/components/TeamLeadView'
import EmployeeView from '@/components/EmployeeView'
import { useApp } from '@/contexts/AppContext'
import { Task } from '@/types'

// Initial mock tasks
const initialTasks: Task[] = [
    {
        id: 1,
        title: 'Design System Audit',
        tag: 'UI',
        assignee: 'JD',
        complexity: 'Medium',
        status: 'In Progress',
    },
    {
        id: 2,
        title: 'API Integration',
        tag: 'Backend',
        assignee: 'SM',
        complexity: 'High',
        status: 'Review',
    },
    {
        id: 3,
        title: 'User Profile Component',
        tag: 'Frontend',
        assignee: 'AK',
        complexity: 'Low',
        status: 'Done',
    },
]

export default function Home() {
    const { role, tasks, setTasks, setHasNewNotification, setShowToast } = useApp()

    // Initialize tasks on first load
    useEffect(() => {
        if (tasks.length === 0) {
            setTasks(initialTasks)
        }
    }, [])

    const handleAIComplete = () => {
        // Add the 3 new tasks when AI pipeline completes
        const newTasks: Task[] = [
            {
                id: Date.now() + 1,
                title: 'Refactor Auth Middleware',
                tag: 'Backend',
                assignee: 'AI',
                complexity: 'High',
                status: 'To Do',
            },
            {
                id: Date.now() + 2,
                title: 'Update Dashboard UI',
                tag: 'Frontend',
                assignee: 'AI',
                complexity: 'Medium',
                status: 'To Do',
            },
            {
                id: Date.now() + 3,
                title: 'Fix Navigation Bug',
                tag: 'UI',
                assignee: 'AI',
                complexity: 'Low',
                status: 'To Do',
            },
        ]

        setTasks([...tasks, ...newTasks])

        // Show notification
        setHasNewNotification(true)
        setShowToast(true)

        // Hide toast after 3 seconds
        setTimeout(() => {
            setShowToast(false)
        }, 3000)
    }

    return (
        <div className="p-8">
            {role === 'teamlead' ? (
                <TeamLeadView onAIComplete={handleAIComplete} />
            ) : (
                <EmployeeView tasks={tasks} />
            )}
        </div>
    )
}
