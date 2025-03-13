import axios from 'axios';

export interface UserQuery {
    username?: string;
    email?: string;
    department?: string;
    role?: string;
}

export interface User {
    id: number;
    username: string;
    email: string;
    full_name: string;
    department: string;
    role: string;
    created_at: string;
    last_login?: string;
}

const api = axios.create({
    baseURL: 'http://localhost:3000'
});

export const searchUsers = async (query: UserQuery, page: number = 1, pageSize: number = 10) => {
    const params = {
        ...query,
        skip: (page - 1) * pageSize,
        limit: pageSize
    };
    
    const response = await api.get<User[]>('/api/users/', { params });
    return response.data;
}; 