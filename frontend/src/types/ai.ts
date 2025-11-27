export interface SubtaskSuggestion {
  title: string;
  description: string;
  assigned_to_user_id: number | null;
  assigned_to_username: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimated_time: string;
  required_skills: string[];
  reasoning: string;
}

export interface ProblemAnalysis {
  problem_summary: string;
  problem_type: string;
  priority: string;
  required_skills: string[];
  estimated_complexity: string;
  keywords: string[];
  language: string;
}

export interface TaskBreakdownResponse {
  analysis_id: number;
  overall_strategy: string;
  subtasks: SubtaskSuggestion[];
  problem_analysis: ProblemAnalysis;
  model_used: string;
  warnings: string[];
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export interface AnalysisHistoryItem {
  id: number;
  problem_description: string;
  status: 'pending' | 'approved' | 'rejected';
  overall_strategy: string;
  subtasks_count: number;
  created_tasks_count: number;
  created_at: string;
  applied_at: string | null;
  model_used: string;
}

export interface AnalysisHistoryResponse {
  total: number;
  items: AnalysisHistoryItem[];
}

export interface CreateBreakdownRequest {
  room_id: number;
  problem_description: string;
  language: 'en' | 'ru';
  use_reasoning_model?: boolean;
}

export interface ApplyBreakdownRequest {
  analysis_id: number;
  selected_subtask_indices?: number[];
}

export interface ApplyBreakdownResponse {
  analysis_id: number;
  created_tasks: Array<{
    task_id: number;
    title: string;
    assigned_to: string | null;
    priority: string;
  }>;
  total_created: number;
  status: string;
  applied_at: string;
}
