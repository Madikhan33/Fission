'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, History, ArrowLeft, Loader2, CheckCircle2 } from 'lucide-react';
import { aiService } from '@/services/ai.service';
import { TaskBreakdownResponse, AnalysisHistoryItem } from '@/types/ai';
import TaskBreakdownView from './TaskBreakdownView';
import AnalysisHistory from './AnalysisHistory';
import { toast } from 'react-hot-toast';
import { useWebSocket } from '@/hooks/useWebSocket';
import AIProgress from '@/components/AIProgress';

interface AIAssistantModalProps {
    isOpen: boolean;
    onClose: () => void;
    roomId: number;
    onTasksCreated: () => void;
}

type View = 'input' | 'processing' | 'review' | 'history';

export default function AIAssistantModal({
    isOpen,
    onClose,
    roomId,
    onTasksCreated
}: AIAssistantModalProps) {
    const [view, setView] = useState<View>('input');
    const [problemDescription, setProblemDescription] = useState('');
    const [language, setLanguage] = useState<'en' | 'ru'>('ru');
    const [useReasoning, setUseReasoning] = useState(false);

    const [analysisResult, setAnalysisResult] = useState<TaskBreakdownResponse | null>(null);
    const [selectedTaskIndices, setSelectedTaskIndices] = useState<number[]>([]);
    const [isApplying, setIsApplying] = useState(false);

    const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(false);
    // ... existing state ...

    // AI Progress State
    const [aiStatus, setAiStatus] = useState<'idle' | 'analyzing' | 'breaking_down' | 'complete' | 'error'>('idle');
    const [aiMessage, setAiMessage] = useState('');

    // WebSocket for AI updates
    const { subscribeToAnalysis } = useWebSocket({
        onMessage: (msg) => {
            if (msg.type === 'ai_progress') {
                if (msg.status) setAiStatus(msg.status as any);
                if (msg.message) setAiMessage(msg.message);

                // If complete, we'll wait for the API response to switch view
                // The API response contains the full breakdown data
            }
        }
    });

    // Reset state when closed
    useEffect(() => {
        if (!isOpen) {
            setView('input');
            setProblemDescription('');
            setAnalysisResult(null);
            setAiStatus('idle');
            setAiMessage('');
        }
    }, [isOpen]);

    const handleAnalyze = async () => {
        if (!problemDescription.trim()) return;

        setView('processing');
        setAiStatus('analyzing');
        setAiMessage('Starting analysis...');

        try {
            const result = await aiService.createBreakdown({
                room_id: roomId,
                problem_description: problemDescription,
                language,
                use_reasoning_model: useReasoning
            });

            setAnalysisResult(result);
            // Select all tasks by default
            setSelectedTaskIndices(result.subtasks.map((_, i) => i));

            setAiStatus('complete');
            setTimeout(() => setView('review'), 500); // Small delay to show completion
        } catch (error) {
            console.error('Analysis failed:', error);
            toast.error('Failed to analyze problem');
            setAiStatus('error');
            setAiMessage('Analysis failed. Please try again.');
            setTimeout(() => setView('input'), 2000);
        }
    };

    // ... existing handlers ...

    // ... render ...
    {
        view === 'processing' && (
            <motion.div
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center h-full py-12 space-y-4 px-8"
            >
                <div className="w-full max-w-md">
                    <AIProgress status={aiStatus} message={aiMessage} />
                </div>
            </motion.div>
        )
    }

    const handleApply = async () => {
        if (!analysisResult) return;

        setIsApplying(true);
        try {
            await aiService.applyBreakdown({
                analysis_id: analysisResult.analysis_id,
                selected_subtask_indices: selectedTaskIndices
            });

            toast.success(`${selectedTaskIndices.length} tasks created successfully`);
            onTasksCreated();
            onClose();
        } catch (error) {
            console.error('Failed to apply breakdown:', error);
            toast.error('Failed to create tasks');
        } finally {
            setIsApplying(false);
        }
    };

    const loadHistory = async () => {
        setView('history');
        setIsLoadingHistory(true);
        try {
            const response = await aiService.getHistory(roomId);
            setHistory(response.items);
        } catch (error) {
            console.error('Failed to load history:', error);
            toast.error('Failed to load history');
        } finally {
            setIsLoadingHistory(false);
        }
    };

    const handleHistorySelect = async (item: AnalysisHistoryItem) => {
        // Load full details
        try {
            const details = await aiService.getAnalysisDetails(item.id);
            setAnalysisResult(details);
            setSelectedTaskIndices(details.subtasks.map((_, i) => i));
            setView('review');
        } catch (error) {
            toast.error('Failed to load analysis details');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden"
            >
                {/* Header */}
                <div className="p-6 border-b border-zinc-100 flex justify-between items-center bg-white z-10">
                    <div className="flex items-center gap-3">
                        {view !== 'input' && (
                            <button
                                onClick={() => setView('input')}
                                className="p-1 hover:bg-zinc-100 rounded-full transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5 text-zinc-500" />
                            </button>
                        )}
                        <div>
                            <h2 className="text-xl font-semibold text-black flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-purple-600" />
                                AI Assistant
                            </h2>
                            <p className="text-xs text-zinc-500">Powered by Reasoning Models</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {view === 'input' && (
                            <button
                                onClick={loadHistory}
                                className="p-2 hover:bg-zinc-100 rounded-full transition-colors text-zinc-500"
                                title="History"
                            >
                                <History className="w-5 h-5" />
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-zinc-100 rounded-full transition-colors text-zinc-500"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    <AnimatePresence mode="wait">
                        {view === 'input' && (
                            <motion.div
                                key="input"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="space-y-6"
                            >
                                <div>
                                    <label className="block text-sm font-medium text-black mb-2">
                                        Describe the problem
                                    </label>
                                    <textarea
                                        value={problemDescription}
                                        onChange={(e) => setProblemDescription(e.target.value)}
                                        placeholder="e.g., The database is slow during peak hours. We need to optimize queries and add indexes..."
                                        className="w-full h-40 p-4 border border-zinc-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent resize-none text-sm"
                                    />
                                </div>

                                <div className="flex gap-6">
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-black mb-2">
                                            Language
                                        </label>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => setLanguage('ru')}
                                                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${language === 'ru'
                                                    ? 'bg-black text-white'
                                                    : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                                                    }`}
                                            >
                                                Русский
                                            </button>
                                            <button
                                                onClick={() => setLanguage('en')}
                                                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${language === 'en'
                                                    ? 'bg-black text-white'
                                                    : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                                                    }`}
                                            >
                                                English
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-black mb-2">
                                            Model Capability
                                        </label>
                                        <div className="flex items-center gap-3 p-2 border border-zinc-200 rounded-lg">
                                            <input
                                                type="checkbox"
                                                checked={useReasoning}
                                                onChange={(e) => setUseReasoning(e.target.checked)}
                                                className="w-4 h-4 text-black rounded border-zinc-300 focus:ring-black"
                                            />
                                            <div className="text-sm">
                                                <span className="font-medium text-black">Use Reasoning Model</span>
                                                <p className="text-xs text-zinc-500">Slower but smarter (o1-mini)</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={handleAnalyze}
                                    disabled={!problemDescription.trim()}
                                    className="w-full py-3 bg-black text-white rounded-lg font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    <Sparkles className="w-4 h-4" />
                                    Analyze & Breakdown
                                </button>
                            </motion.div>
                        )}

                        {view === 'processing' && (
                            <motion.div
                                key="processing"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex flex-col items-center justify-center h-full py-12 space-y-4 px-8"
                            >
                                <div className="w-full max-w-md">
                                    <AIProgress status={aiStatus} message={aiMessage} />
                                </div>
                            </motion.div>
                        )}

                        {view === 'review' && analysisResult && (
                            <motion.div
                                key="review"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                            >
                                <TaskBreakdownView
                                    subtasks={analysisResult.subtasks}
                                    selectedIndices={selectedTaskIndices}
                                    onToggleSelection={(index) => {
                                        setSelectedTaskIndices(prev =>
                                            prev.includes(index)
                                                ? prev.filter(i => i !== index)
                                                : [...prev, index]
                                        );
                                    }}
                                    overallStrategy={analysisResult.overall_strategy}
                                    modelUsed={analysisResult.model_used}
                                />
                            </motion.div>
                        )}

                        {view === 'history' && (
                            <motion.div
                                key="history"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <AnalysisHistory
                                    items={history}
                                    onSelect={handleHistorySelect}
                                    isLoading={isLoadingHistory}
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Footer Actions (Review Mode Only) */}
                {view === 'review' && (
                    <div className="p-6 border-t border-zinc-100 bg-zinc-50 flex justify-between items-center">
                        <div className="text-sm text-zinc-500">
                            {selectedTaskIndices.length} tasks selected
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setView('input')}
                                className="px-4 py-2 text-sm font-medium text-zinc-600 hover:text-black transition-colors"
                            >
                                Cancel
                            </button>
                            {analysisResult?.status !== 'approved' && (
                                <button
                                    onClick={handleApply}
                                    disabled={selectedTaskIndices.length === 0 || isApplying}
                                    className="px-6 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 flex items-center gap-2"
                                >
                                    {isApplying ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <CheckCircle2 className="w-4 h-4" />
                                    )}
                                    Apply & Create Tasks
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
