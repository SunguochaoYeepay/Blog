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
    last_login: string | null;
    password?: string;
}

export interface UserCreate {
    username: string;
    email: string;
    full_name: string;
    department: string;
    role: string;
    password: string;
} 