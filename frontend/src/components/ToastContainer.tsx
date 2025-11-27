'use client'

import { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, Bell } from 'lucide-react'

export type ToastType = 'success' | 'error' | 'info' | 'notification'

interface ToastData {
    id: string
    type: ToastType
    title: string
    message: string
    duration?: number
}

interface ToastProps {
    toast: ToastData
    onClose: (id: string) => void
}

function Toast({ toast, onClose }: ToastProps) {
    const [isExiting, setIsExiting] = useState(false)

    useEffect(() => {
        const duration = toast.duration || 5000
        const timer = setTimeout(() => {
            handleClose()
        }, duration)

        return () => clearTimeout(timer)
    }, [toast])

    const handleClose = () => {
        setIsExiting(true)
        setTimeout(() => {
            onClose(toast.id)
        }, 300)
    }

    const getIcon = () => {
        switch (toast.type) {
            case 'success':
                return <CheckCircle className="w-5 h-5 text-green-600" />
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-600" />
            case 'notification':
                return <Bell className="w-5 h-5 text-blue-600" />
            default:
                return <Info className="w-5 h-5 text-blue-600" />
        }
    }

    const getBorderColor = () => {
        switch (toast.type) {
            case 'success':
                return 'border-l-green-500'
            case 'error':
                return 'border-l-red-500'
            case 'notification':
                return 'border-l-blue-500'
            default:
                return 'border-l-blue-500'
        }
    }

    return (
        <div
            className={`
                bg-white border-l-4 ${getBorderColor()} rounded-lg shadow-lg p-4 mb-3 min-w-[320px] max-w-md
                transition-all duration-300 transform
                ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
            `}
        >
            <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                    {getIcon()}
                </div>

                <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-black mb-1">
                        {toast.title}
                    </h4>
                    <p className="text-sm text-zinc-600">
                        {toast.message}
                    </p>
                </div>

                <button
                    onClick={handleClose}
                    className="flex-shrink-0 p-1 hover:bg-zinc-100 rounded transition-colors"
                >
                    <X className="w-4 h-4 text-zinc-400" />
                </button>
            </div>
        </div>
    )
}

export default function ToastContainer() {
    const [toasts, setToasts] = useState<ToastData[]>([])

    // Global function to show toast
    useEffect(() => {
        // @ts-ignore
        window.showToast = (title: string, message: string, type: ToastType = 'info', duration?: number) => {
            const id = Math.random().toString(36).substring(7)
            setToasts(prev => [...prev, { id, title, message, type, duration }])
        }

        return () => {
            // @ts-ignore
            delete window.showToast
        }
    }, [])

    const handleClose = (id: string) => {
        setToasts(prev => prev.filter(toast => toast.id !== id))
    }

    if (toasts.length === 0) return null

    return (
        <div className="fixed top-4 right-4 z-[9999] pointer-events-none">
            <div className="pointer-events-auto">
                {toasts.map(toast => (
                    <Toast key={toast.id} toast={toast} onClose={handleClose} />
                ))}
            </div>
        </div>
    )
}

// Type declaration for global window
declare global {
    interface Window {
        showToast: (title: string, message: string, type?: ToastType, duration?: number) => void
    }
}
