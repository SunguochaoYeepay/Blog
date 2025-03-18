export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string
  department: string
  role: string
  created_at: string
  last_login: string | null
}