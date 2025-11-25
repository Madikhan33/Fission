'use client'

import { useState } from 'react'
import { Sparkles } from 'lucide-react'
import AIAgentModal from './AIAgentModal'
import { TeamLeadViewProps } from '@/types'

export default function TeamLeadView({ onAIComplete }: TeamLeadViewProps) {
    const [isModalOpen, setIsModalOpen] = useState(false)

    const handleOpenModal = () => {
        setIsModalOpen(true)
    }

    const handleCloseModal = () => {
        setIsModalOpen(false)
    }

    const handleComplete = () => {
        onAIComplete()
        handleCloseModal()
    }

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-12">
                <h1 className="text-4xl font-bold text-black mb-3">Team Lead Dashboard</h1>
                <p className="text-zinc-500 text-lg">
                    Deploy AI agents to analyze context and automatically generate tasks for your team.
                </p>
            </div>

            {/* Main Action Card */}
            <div className="bg-white border border-zinc-200 rounded-lg p-12 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-center max-w-xl mx-auto">
                    <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-6">
                        <Sparkles className="w-8 h-8 text-white" />
                    </div>

                    <h2 className="text-2xl font-semibold text-black mb-3">
                        AI Task Generation
                    </h2>

                    <p className="text-zinc-600 mb-8">
                        Provide project context and let our AI pipeline analyze, classify, and assign tasks to the right team members automatically.
                    </p>

                    <button
                        onClick={handleOpenModal}
                        className="bg-black text-white px-8 py-3.5 rounded-lg font-medium hover:bg-zinc-800 transition-colors shadow-sm text-base"
                    >
                        Deploy AI Agent
                    </button>
                </div>
            </div>

            {/* Info Cards */}
            <div className="grid grid-cols-3 gap-6 mt-8">
                <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
                    <div className="text-2xl font-bold text-black mb-1">8</div>
                    <div className="text-sm text-zinc-600">Pipeline Steps</div>
                </div>
                <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
                    <div className="text-2xl font-bold text-black mb-1">~6s</div>
                    <div className="text-sm text-zinc-600">Avg. Processing Time</div>
                </div>
                <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
                    <div className="text-2xl font-bold text-black mb-1">100%</div>
                    <div className="text-sm text-zinc-600">Automated</div>
                </div>
            </div>

            {/* AI Agent Modal */}
            {isModalOpen && (
                <AIAgentModal
                    onClose={handleCloseModal}
                    onComplete={handleComplete}
                />
            )}
        </div>
    )
}
