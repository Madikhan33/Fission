import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to add the auth token to headers
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Prevent caching
        config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
        config.headers['Pragma'] = 'no-cache';
        config.headers['Expires'] = '0';

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle 401 errors (token expired/invalid)
api.interceptors.response.use(
    (response) => {
        // Return successful responses as-is
        return response;
    },
    (error) => {
        // Check if error is 401 Unauthorized
        if (error.response && error.response.status === 401) {
            // Clear token and redirect to login
            localStorage.removeItem('token');

            // Only redirect if not already on auth page
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/auth')) {
                window.location.href = '/auth';
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authApi = {
    // Login with username and password (JSON)
    login: async (username: string, password: string) => {
        const response = await api.post('/auth/login', {
            username,
            password
        });
        return response.data;
    },

    // Register new user
    register: async (username: string, email: string, password: string) => {
        const response = await api.post('/auth/register', {
            username,
            email,
            password
        });
        return response.data;
    },

    // Get current user info
    getMe: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    // Logout
    logout: async () => {
        const response = await api.post('/auth/logout');
        return response.data;
    },

    // Get all users
    getAllUsers: async () => {
        const response = await api.get('/auth/users');
        return response.data;
    },

    // Get team members (users in same rooms)
    getTeamMembers: async () => {
        const response = await api.get('/auth/team-members');
        return response.data;
    }
};

// Tasks API
export const tasksApi = {
    // Get all tasks with filters and pagination
    getAll: async (params?: {
        status?: string;
        priority?: string;
        page?: number;
        page_size?: number;
        room_id?: number;
    }) => {
        const response = await api.get('/tasks/', { params });
        return response.data;
    },

    // Get my tasks (where I'm assigned)
    getMyTasks: async (params?: { page?: number; page_size?: number }) => {
        const response = await api.get('/tasks/my', { params });
        return response.data;
    },

    // Get tasks created by me
    getCreatedByMe: async (params?: { page?: number; page_size?: number }) => {
        const response = await api.get('/tasks/created-by-me', { params });
        return response.data;
    },

    // Get overdue tasks
    getOverdue: async () => {
        const response = await api.get('/tasks/overdue');
        return response.data;
    },

    // Get task by ID
    getById: async (id: number) => {
        const response = await api.get(`/tasks/${id}`);
        return response.data;
    },

    // Create new task
    create: async (data: {
        title: string;
        description?: string;
        status?: string;
        priority?: string;
        assignee_ids?: number[];
        room_id?: number;
    }) => {
        const response = await api.post('/tasks/', data);
        return response.data;
    },

    // Update task
    update: async (id: number, data: {
        title?: string;
        description?: string;
        status?: string;
        priority?: string;
    }) => {
        const response = await api.put(`/tasks/${id}`, data);
        return response.data;
    },

    // Update task status only
    updateStatus: async (id: number, status: string) => {
        const response = await api.patch(`/tasks/${id}/status`, { status });
        return response.data;
    },

    // Delete task
    delete: async (id: number) => {
        const response = await api.delete(`/tasks/${id}`);
        return response.data;
    },

    // Add assignee to task
    addAssignee: async (taskId: number, userId: number) => {
        const response = await api.post(`/tasks/${taskId}/assignees`, { user_id: userId });
        return response.data;
    },

    // Remove assignee from task
    removeAssignee: async (taskId: number, userId: number) => {
        const response = await api.delete(`/tasks/${taskId}/assignees/${userId}`);
        return response.data;
    },

    // Bulk assign users to task
    bulkAssign: async (taskId: number, userIds: number[]) => {
        const response = await api.post(`/tasks/${taskId}/assignees/bulk`, { user_ids: userIds });
        return response.data;
    },

    // Get my statistics
    getMyStats: async () => {
        const response = await api.get('/tasks/statistics/me');
        return response.data;
    },

    // Get user statistics (for leads)
    getUserStats: async (userId: number) => {
        const response = await api.get(`/tasks/statistics/user/${userId}`);
        return response.data;
    },

    // Search tasks
    search: async (query: string) => {
        const response = await api.get('/tasks/search', { params: { q: query } });
        return response.data;
    }
};

// Rooms API
export const roomsApi = {
    // Get all rooms where user is a member
    getAll: async () => {
        const response = await api.get('/rooms/get_all');
        return response.data;
    },

    // Get room by ID
    getById: async (id: number) => {
        const response = await api.get(`/rooms/${id}`);
        return response.data;
    },

    // Create new room
    create: async (data: {
        name: string;
        description?: string;
    }) => {
        const response = await api.post('/rooms/create', data);
        return response.data;
    },

    // Update room
    update: async (id: number, data: {
        name?: string;
        description?: string;
    }) => {
        const response = await api.put(`/rooms/${id}`, data);
        return response.data;
    },

    // Delete room
    delete: async (id: number) => {
        const response = await api.delete(`/rooms/${id}`);
        return response.data;
    },

    // Get room members
    getMembers: async (roomId: number) => {
        const response = await api.get(`/rooms/${roomId}/members`);
        return response.data;
    },

    // Add member to room
    addMember: async (roomId: number, data: {
        user_id: number;
        role?: 'owner' | 'admin' | 'member';
    }) => {
        const response = await api.post(`/rooms/${roomId}/members`, data);
        return response.data;
    },

    // Remove member from room
    removeMember: async (roomId: number, userId: number) => {
        const response = await api.delete(`/rooms/${roomId}/members/${userId}`);
        return response.data;
    },

    // Update member role
    updateMemberRole: async (roomId: number, userId: number, role: 'admin' | 'member') => {
        const response = await api.patch(`/rooms/${roomId}/members/${userId}/role`, { role });
        return response.data;
    }
};

// Notifications API
export const notificationsApi = {
    // Get notifications
    getAll: async (unreadOnly: boolean = false, limit: number = 50) => {
        const response = await api.get('/notifications/', {
            params: { unread_only: unreadOnly, limit }
        });
        return response.data;
    },

    // Get unread count
    getUnreadCount: async () => {
        const response = await api.get('/notifications/unread-count');
        return response.data.count;
    },

    // Mark notifications as read
    markAsRead: async (notificationIds: number[]) => {
        const response = await api.post('/notifications/mark-read', {
            notification_ids: notificationIds
        });
        return response.data;
    },

    // Delete notification
    delete: async (notificationId: number) => {
        const response = await api.delete(`/notifications/${notificationId}`);
        return response.data;
    }
};

export default api;
