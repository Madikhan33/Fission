import React from 'react';
import { SubtaskSuggestion } from '@/types/ai';
import { CheckCircle2, Clock, User, AlertTriangle, Calendar, BarChart } from 'lucide-react';

interface TaskBreakdownViewProps {
    subtasks: SubtaskSuggestion[];
    selectedIndices: number[];
    onToggleSelection: (index: number) => void;
    overallStrategy: string;
    modelUsed: string;
}

function getComplexityLabel(score?: number) {
    if (!score) return 'Not set';
    if (score <= 2) return 'Trivial';
    if (score <= 4) return 'Simple';
    if (score <= 6) return 'Moderate';
    if (score <= 8) return 'Complex';
    return 'Very Complex';
}

function getComplexityColor(score?: number) {
    if (!score) return 'bg-zinc-100 text-zinc-600';
    if (score <= 2) return 'bg-green-100 text-green-700';
    if (score <= 4) return 'bg-blue-100 text-blue-700';
    if (score <= 6) return 'bg-yellow-100 text-yellow-700';
    if (score <= 8) return 'bg-orange-100 text-orange-700';
    return 'bg-red-100 text-red-700';
}

export default function TaskBreakdownView({
    subtasks,
    selectedIndices,
    onToggleSelection,
    overallStrategy,
    modelUsed
}: TaskBreakdownViewProps) {
    return (
        <div className="space-y-6">
            {/* Strategy Section */}
            <div className="bg-zinc-50 p-4 rounded-lg border border-zinc-200">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-black">AI Strategy</h3>
                    <span className="text-xs px-2 py-1 bg-zinc-200 rounded text-zinc-600 font-mono">
                        {modelUsed}
                    </span>
                </div>
                <p className="text-sm text-zinc-600 leading-relaxed">{overallStrategy}</p>
            </div>

            {/* Tasks List */}
            <div className="space-y-3">
                <h3 className="font-medium text-black flex items-center gap-2">
                    Suggested Tasks
                    <span className="text-sm font-normal text-zinc-500">
                        ({selectedIndices.length} selected)
                    </span>
                </h3>

                <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                    {subtasks.map((task, index) => {
                        const isSelected = selectedIndices.includes(index);

                        return (
                            <div
                                key={index}
                                onClick={() => onToggleSelection(index)}
                                className={`p-4 rounded-lg border cursor-pointer transition-all ${isSelected
                                    ? 'bg-black/5 border-black'
                                    : 'bg-white border-zinc-200 hover:border-zinc-300'
                                    }`}
                            >
                                <div className="flex items-start gap-3">
                                    {/* Checkbox */}
                                    <div className={`mt-1 w-5 h-5 rounded border flex items-center justify-center transition-colors ${isSelected ? 'bg-black border-black' : 'border-zinc-300'
                                        }`}>
                                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 space-y-2">
                                        <div className="flex justify-between items-start">
                                            <h4 className="font-medium text-black">{task.title}</h4>
                                            <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${task.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                                                task.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                                                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                                        'bg-green-100 text-green-700'
                                                }`}>
                                                {task.priority}
                                            </span>
                                        </div>

                                        <p className="text-sm text-zinc-600">{task.description}</p>

                                        <div className="flex flex-wrap gap-3 text-xs text-zinc-500 pt-1">
                                            {task.assigned_to_username ? (
                                                <div className="flex items-center gap-1 text-black font-medium">
                                                    <User className="w-3.5 h-3.5" />
                                                    {task.assigned_to_username}
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-1 text-orange-600">
                                                    <AlertTriangle className="w-3.5 h-3.5" />
                                                    Unassigned
                                                </div>
                                            )}

                                            <div className="flex items-center gap-1">
                                                <Clock className="w-3.5 h-3.5" />
                                                {task.estimated_time}
                                                {task.estimated_hours && ` (~${task.estimated_hours}h)`}
                                            </div>

                                            {task.due_date_days && (
                                                <div className="flex items-center gap-1 text-blue-600">
                                                    <Calendar className="w-3.5 h-3.5" />
                                                    Due in {task.due_date_days} days
                                                </div>
                                            )}

                                            {task.complexity_score && (
                                                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded ${getComplexityColor(task.complexity_score)}`}>
                                                    <BarChart className="w-3.5 h-3.5" />
                                                    {getComplexityLabel(task.complexity_score)} ({task.complexity_score}/10)
                                                </div>
                                            )}
                                        </div>

                                        {/* Reasoning */}
                                        <div className="text-xs bg-zinc-50 p-2 rounded text-zinc-600 italic">
                                            "{task.reasoning}"
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
