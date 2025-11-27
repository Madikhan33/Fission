'use client'

import { useState, useEffect } from 'react'
import { Bell, X, Check, Trash2 } from 'lucide-react'
import { Notification } from '@/types'
import { notificationsApi } from '@/services/api'
import { useRouter } from 'next/navigation'

export default function NotificationBell() {
    const router = useRouter()
    const [isOpen, setIsOpen] = useState(false)
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [unreadCount, setUnreadCount] = useState(0)
    const [loading, setLoading] = useState(false)

    // Fetch notifications
    const fetchNotifications = async () => {
        try {
            const data = await notificationsApi.getAll(false, 20)
            setNotifications(data)

            const count = await notificationsApi.getUnreadCount()
            setUnreadCount(count)
        } catch (error) {
            console.error('Failed to fetch notifications:', error)
        }
    }

    useEffect(() => {
        fetchNotifications()

        // Refresh every 30 seconds
        const interval = setInterval(fetchNotifications, 30000)
        return () => clearInterval(interval)
    }, [])

    const handleMarkAsRead = async (notificationId: number) => {
        try {
            await notificationsApi.markAsRead([notificationId])
            fetchNotifications()
        } catch (error) {
            console.error('Failed to mark as read:', error)
        }
    }

    const handleMarkAllAsRead = async () => {
        try {
            const unreadIds = notifications
                .filter(n => !n.is_read)
                .map(n => n.id)

            if (unreadIds.length > 0) {
                await notificationsApi.markAsRead(unreadIds)
                fetchNotifications()
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error)
        }
    }

    const handleDelete = async (notificationId: number) => {
        try {
            await notificationsApi.delete(notificationId)
            fetchNotifications()
        } catch (error) {
            console.error('Failed to delete notification:', error)
        }
    }

    const handleNotificationClick = (notification: Notification) => {
        if (!notification.is_read) {
            handleMarkAsRead(notification.id)
        }

        if (notification.link_url) {
            router.push(notification.link_url)
            setIsOpen(false)
        }
    }

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'task_assigned':
                return '📋'
            case 'task_updated':
                return '🔄'
            case 'task_completed':
                return '✅'
            case 'room_invite':
                return '🏠'
            case 'ai_analysis_complete':
                return '🤖'
            default:
                return '📢'
        }
    }

    const formatTime = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)

        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins}m ago`

        const diffHours = Math.floor(diffMins / 60)
        if (diffHours < 24) return `${diffHours}h ago`

        const diffDays = Math.floor(diffHours / 24)
        return `${diffDays}d ago`
    }

    return (
        <div className="relative">
            {/* Bell Icon */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 hover:bg-zinc-100 rounded-lg transition-colors"
            >
                <Bell className="w-5 h-5 text-zinc-600" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-semibold">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {/* Dropdown Panel */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Panel */}
                    <div className="absolute right-0 mt-2 w-96 bg-white border border-zinc-200 rounded-lg shadow-xl z-50 max-h-[600px] flex flex-col">
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-zinc-200">
                            <h3 className="font-semibold text-black">Notifications</h3>
                            <div className="flex items-center gap-2">
                                {unreadCount > 0 && (
                                    <button
                                        onClick={handleMarkAllAsRead}
                                        className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                                    >
                                        Mark all read
                                    </button>
                                )}
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-1 hover:bg-zinc-100 rounded"
                                >
                                    <X className="w-4 h-4 text-zinc-500" />
                                </button>
                            </div>
                        </div>

                        {/* List */}
                        <div className="overflow-y-auto flex-1">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-zinc-500">
                                    <Bell className="w-12 h-12 mx-auto mb-3 text-zinc-300" />
                                    <p>No notifications yet</p>
                                </div>
                            ) : (
                                notifications.map((notification) => (
                                    <div
                                        key={notification.id}
                                        className={`p-4 border-b border-zinc-100 hover:bg-zinc-50 transition-colors cursor-pointer group ${!notification.is_read ? 'bg-blue-50' : ''
                                            }`}
                                        onClick={() => handleNotificationClick(notification)}
                                    >
                                        <div className="flex items-start gap-3">
                                            {/* Icon */}
                                            <div className="text-2xl flex-shrink-0">
                                                {getNotificationIcon(notification.type)}
                                            </div>

                                            {/* Content */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-2">
                                                    <h4 className="text-sm font-semibold text-black">
                                                        {notification.title}
                                                    </h4>
                                                    {!notification.is_read && (
                                                        <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                                                    )}
                                                </div>
                                                <p className="text-xs text-zinc-600 mt-1 line-clamp-2">
                                                    {notification.message}
                                                </p>
                                                <p className="text-xs text-zinc-400 mt-1">
                                                    {formatTime(notification.created_at)}
                                                </p>
                                            </div>

                                            {/* Actions */}
                                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                {!notification.is_read && (
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation()
                                                            handleMarkAsRead(notification.id)
                                                        }}
                                                        className="p-1 hover:bg-white rounded"
                                                        title="Mark as read"
                                                    >
                                                        <Check className="w-4 h-4 text-green-600" />
                                                    </button>
                                                )}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation()
                                                        handleDelete(notification.id)
                                                    }}
                                                    className="p-1 hover:bg-white rounded"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="w-4 h-4 text-red-600" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
