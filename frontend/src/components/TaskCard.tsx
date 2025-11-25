'use client'

import { motion } from 'framer-motion'
import { TaskCardProps } from '@/types'

const tagColors: Record<string, string> = {
    'Frontend': 'bg-zinc-100 text-zinc-700',
    'Backend': 'bg-zinc-200 text-zinc-800',
    'UI': 'bg-zinc-100 text-zinc-600',
}

const complexityColors: Record<string, string> = {
    'Low': 'border-zinc-300 text-zinc-600',
    'Medium': 'border-zinc-400 text-zinc-700',
    'High': 'border-zinc-600 text-zinc-900',
}

export default function TaskCard({ task }: TaskCardProps) {
    const { title, tag, assignee, complexity } = task

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -2 }}
            transition={{ duration: 0.2 }}
            className="bg-white border border-zinc-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-all cursor-pointer"
        >
            {/* Title */}
            <h3 className="text-sm font-semibold text-black mb-3 leading-snug">
                {title}
            </h3>

            {/* Tag */}
            <div className="mb-3">
                <span className={`inline-block px-2.5 py-1 rounded text-xs font-medium ${tagColors[tag] || 'bg-zinc-100 text-zinc-600'}`}>
                    {tag}
                </span>
            </div>

            {/* Footer: Assignee + Complexity */}
            <div className="flex items-center justify-between pt-3 border-t border-zinc-100">
                {/* Assignee Avatar */}
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-black text-white flex items-center justify-center text-xs font-medium">
                        {assignee}
                    </div>
                </div>

                {/* Complexity Badge */}
                <span className={`text-xs font-medium px-2 py-0.5 rounded border ${complexityColors[complexity] || 'border-zinc-300 text-zinc-600'}`}>
                    {complexity}
                </span>
            </div>
        </motion.div>
    )
}
