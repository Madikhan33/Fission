import React from 'react';
import { AnalysisHistoryItem } from '@/types/ai';
import { Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

interface AnalysisHistoryProps {
    items: AnalysisHistoryItem[];
    onSelect: (item: AnalysisHistoryItem) => void;
    isLoading: boolean;
}

export default function AnalysisHistory({ items, onSelect, isLoading }: AnalysisHistoryProps) {
    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-zinc-400" />
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="text-center py-12 text-zinc-500">
                No analysis history yet.
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {items.map((item) => (
                <div
                    key={item.id}
                    onClick={() => onSelect(item)}
                    className="p-4 bg-white border border-zinc-200 rounded-lg hover:border-black transition-colors cursor-pointer group"
                >
                    <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${item.status === 'approved' ? 'bg-green-500' :
                                    item.status === 'rejected' ? 'bg-red-500' :
                                        'bg-yellow-500'
                                }`} />
                            <span className="font-medium text-sm text-black">
                                Analysis #{item.id}
                            </span>
                        </div>
                        <span className="text-xs text-zinc-400">
                            {format(new Date(item.created_at), 'MMM d, HH:mm')}
                        </span>
                    </div>

                    <p className="text-sm text-zinc-600 line-clamp-2 mb-3">
                        {item.problem_description}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-zinc-500">
                        <div className="flex items-center gap-1">
                            <span className="font-mono bg-zinc-100 px-1.5 py-0.5 rounded">
                                {item.model_used}
                            </span>
                        </div>
                        <div>
                            {item.subtasks_count} suggested tasks
                        </div>
                        {item.status === 'approved' && (
                            <div className="flex items-center gap-1 text-green-600">
                                <CheckCircle2 className="w-3 h-3" />
                                Applied
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
