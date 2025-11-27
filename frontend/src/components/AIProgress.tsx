'use client'

import { Loader2, Brain, CheckCircle, AlertCircle } from 'lucide-react'

interface AIProgressProps {
    status: 'idle' | 'analyzing' | 'breaking_down' | 'complete' | 'error'
    message?: string
}

export default function AIProgress({ status, message }: AIProgressProps) {
    if (status === 'idle') return null

    const getStatusConfig = () => {
        switch (status) {
            case 'analyzing':
                return {
                    icon: <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />,
                    title: 'Analyzing Problem',
                    color: 'bg-blue-50 border-blue-200',
                    textColor: 'text-blue-800'
                }
            case 'breaking_down':
                return {
                    icon: <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />,
                    title: 'Creating Task Breakdown',
                    color: 'bg-purple-50 border-purple-200',
                    textColor: 'text-purple-800'
                }
            case 'complete':
                return {
                    icon: <CheckCircle className="w-5 h-5 text-green-600" />,
                    title: 'Analysis Complete',
                    color: 'bg-green-50 border-green-200',
                    textColor: 'text-green-800'
                }
            case 'error':
                return {
                    icon: <AlertCircle className="w-5 h-5 text-red-600" />,
                    title: 'Analysis Failed',
                    color: 'bg-red-50 border-red-200',
                    textColor: 'text-red-800'
                }
            default:
                return {
                    icon: <Brain className="w-5 h-5 text-zinc-600" />,
                    title: 'Processing',
                    color: 'bg-zinc-50 border-zinc-200',
                    textColor: 'text-zinc-800'
                }
        }
    }

    const config = getStatusConfig()

    return (
        <div className={`${config.color} border rounded-lg p-4 mb-4 transition-all duration-300`}>
            <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                    {config.icon}
                </div>

                <div className="flex-1">
                    <h4 className={`text-sm font-semibold ${config.textColor}`}>
                        {config.title}
                    </h4>
                    {message && (
                        <p className="text-xs text-zinc-600 mt-1">
                            {message}
                        </p>
                    )}
                </div>
            </div>

            {/* Progress bar for active states */}
            {(status === 'analyzing' || status === 'breaking_down') && (
                <div className="mt-3 h-1 bg-white rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 animate-progress"
                        style={{
                            animation: 'progress 2s ease-in-out infinite'
                        }}
                    />
                </div>
            )}

            <style jsx>{`
                @keyframes progress {
                    0% {
                        transform: translateX(-100%);
                    }
                    100% {
                        transform: translateX(100%);
                    }
                }
                .animate-progress {
                    width: 50%;
                }
            `}</style>
        </div>
    )
}
