'use client'

import { motion } from 'framer-motion'
import { CheckCircle2 } from 'lucide-react'
import { ToastProps } from '@/types'

export default function Toast({ message }: ToastProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: 50, x: '-50%' }}
            className="fixed bottom-8 left-1/2 bg-black text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 z-50"
        >
            <CheckCircle2 className="w-5 h-5" />
            <span className="text-sm font-medium">{message}</span>
        </motion.div>
    )
}
