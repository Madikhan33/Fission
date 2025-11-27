import api from './api';
import {
    TaskBreakdownResponse,
    CreateBreakdownRequest,
    ApplyBreakdownResponse,
    ApplyBreakdownRequest,
    AnalysisHistoryResponse
} from '@/types/ai';

export const aiService = {
    // Analyze problem and create breakdown
    createBreakdown: async (data: CreateBreakdownRequest): Promise<TaskBreakdownResponse> => {
        const response = await api.post('/ai/breakdown-task', data);
        return response.data;
    },

    // Apply breakdown (create tasks)
    applyBreakdown: async (data: ApplyBreakdownRequest): Promise<ApplyBreakdownResponse> => {
        const response = await api.post('/ai/apply-breakdown', data);
        return response.data;
    },

    // Get history
    getHistory: async (roomId: number, limit = 20, offset = 0): Promise<AnalysisHistoryResponse> => {
        const response = await api.get(`/ai/history/${roomId}`, {
            params: { limit, offset }
        });
        return response.data;
    },

    // Get specific analysis details
    getAnalysisDetails: async (analysisId: number): Promise<TaskBreakdownResponse> => {
        const response = await api.get(`/ai/analysis/${analysisId}`);
        return response.data;
    },

    // Delete analysis
    deleteAnalysis: async (analysisId: number): Promise<void> => {
        await api.delete(`/ai/history/${analysisId}`);
    }
};
