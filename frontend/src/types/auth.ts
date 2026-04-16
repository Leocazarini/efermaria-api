export interface UserProfile {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
  last_login: string | null
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface TokenPair {
  access: string
  refresh: string
}
