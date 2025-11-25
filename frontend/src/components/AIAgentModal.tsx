'use client'

import { useState, useEffect, ChangeEvent } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Upload, Loader2, CheckCircle2 } from 'lucide-react'
import { AIAgentModalProps, PipelineStep } from '@/types'

const pipelineSteps: PipelineStep[] = [
    { id: 1, name: 'Context Collector', duration: 600 },
    { id: 2, name: 'Problem Analyzer', duration: 800 },
    { id: 3, name: 'Query Engineer (Vector questions)', duration: 900 },
    { id: 4, name: 'Vector Search (History/Docs)', duration: 1000 },
    { id: 5, name: 'Task Classifier', duration: 700 },
    { id: 6, name: 'Department Router', duration: 600 },
    { id: 7, name: 'Assignee Selector', duration: 800 },
    { id: 8, name: 'Task Writer (Finalizing)', duration: 900 },
]

type Phase = 'input' | 'processing'

export default function AIAgentModal({ onClose, onComplete }: AIAgentModalProps) {
    const [phase, setPhase] = useState<Phase>('input')
    const [context, setContext] = useState('')
    const [currentStep, setCurrentStep] = useState(0)
    const [completedSteps, setCompletedSteps] = useState<number[]>([])

    const handleStartAnalysis = () => {
        if (!context.trim()) return
        setPhase('processing')
        runPipeline()
    }

    const runPipeline = () => {
        let stepIndex = 0

        const executeStep = () => {
            if (stepIndex < pipelineSteps.length) {
                setCurrentStep(stepIndex)

                setTimeout(() => {
                    setCompletedSteps(prev => [...prev, stepIndex])
                    stepIndex++
                    executeStep()
                }, pipelineSteps[stepIndex].duration)
            } else {
                // All steps complete
                setTimeout(() => {
                    onComplete()
                }, 500)
            }
        }

        executeStep()
    }

    return (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-zinc-200">
                    <h2 className="text-xl font-semibold text-black">
                        {phase === 'input' ? 'Deploy AI Agent' : 'AI Pipeline Processing'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-zinc-100 rounded transition-colors"
                        aria-label="Close modal"
                    >
                        <X className="w-5 h-5 text-zinc-600" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {phase === 'input' ? (
                        <InputPhase
                            context={context}
                            setContext={setContext}
                            onStart={handleStartAnalysis}
                        />
                    ) : (
                        <ProcessingPhase
                            steps={pipelineSteps}
                            currentStep={currentStep}
                            completedSteps={completedSteps}
                        />
                    )}
                </div>
            </motion.div>
        </div>
    )
}

interface InputPhaseProps {
    context: string
    setContext: (value: string) => void
    onStart: () => void
}

function InputPhase({ context, setContext, onStart }: InputPhaseProps) {
    return (
        <div className="space-y-6">
            {/* Project Context Input */}
            <div>
                <label className="block text-sm font-medium text-black mb-2">
                    Project Context
                </label>
                <textarea
                    value={context}
                    onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setContext(e.target.value)}
                    placeholder="Describe your project requirements, goals, and any relevant context..."
                    className="w-full h-32 px-4 py-3 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent resize-none text-sm"
                />
            </div>

            {/* Upload Media Area */}
            <div>
                <label className="block text-sm font-medium text-black mb-2">
                    Upload Media (Optional)
                </label>
                <div className="border-2 border-dashed border-zinc-300 rounded-lg p-8 text-center hover:border-zinc-400 transition-colors cursor-pointer">
                    <Upload className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
                    <p className="text-sm text-zinc-600">
                        Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-zinc-400 mt-1">
                        PNG, JPG, PDF up to 10MB
                    </p>
                </div>
            </div>

            {/* Start Button */}
            <button
                onClick={onStart}
                disabled={!context.trim()}
                className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-zinc-800 transition-colors disabled:bg-zinc-300 disabled:cursor-not-allowed"
            >
                Start Analysis
            </button>
        </div>
    )
}

interface ProcessingPhaseProps {
    steps: PipelineStep[]
    currentStep: number
    completedSteps: number[]
}

function ProcessingPhase({ steps, currentStep, completedSteps }: ProcessingPhaseProps) {
    return (
        <div className="space-y-3 max-h-[60vh] overflow-y-auto">
            {steps.map((step, index) => {
                const isCompleted = completedSteps.includes(index)
                const isActive = currentStep === index && !isCompleted

                return (
                    <motion.div
                        key={step.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`flex items-center gap-4 p-4 rounded-lg border transition-all ${isCompleted
                                ? 'bg-zinc-50 border-zinc-200'
                                : isActive
                                    ? 'bg-white border-black'
                                    : 'bg-white border-zinc-200'
                            }`}
                    >
                        {/* Step Number/Icon */}
                        <div className="flex-shrink-0">
                            {isCompleted ? (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                                >
                                    <CheckCircle2 className="w-6 h-6 text-black" />
                                </motion.div>
                            ) : isActive ? (
                                <Loader2 className="w-6 h-6 text-black animate-spin" />
                            ) : (
                                <div className="w-6 h-6 rounded-full border-2 border-zinc-300 flex items-center justify-center">
                                    <span className="text-xs text-zinc-400 font-medium">{step.id}</span>
                                </div>
                            )}
                        </div>

                        {/* Step Name */}
                        <div className="flex-1">
                            <p className={`text-sm font-medium ${isCompleted || isActive ? 'text-black' : 'text-zinc-400'
                                }`}>
                                {step.name}
                            </p>
                        </div>

                        {/* Status Badge */}
                        {isActive && (
                            <motion.span
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="text-xs text-zinc-500 font-medium"
                            >
                                Processing...
                            </motion.span>
                        )}
                    </motion.div>
                )
            })}
        </div>
    )
}
