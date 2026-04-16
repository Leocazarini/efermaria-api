import { api } from '../lib/axios'
import type { LoginCredentials, TokenPair, UserProfile } from '../types/auth'

export interface RegisterPayload {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  password_confirm: string
}

export async function register(payload: RegisterPayload): Promise<void> {
  await api.post('/api/auth/register/', payload)
}

export async function login(credentials: LoginCredentials): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>('/api/auth/login/', credentials)
  return data
}

export async function getMe(): Promise<UserProfile> {
  const { data } = await api.get<UserProfile>('/api/auth/me/')
  return data
}

export async function changePassword(payload: {
  old_password: string
  new_password: string
}): Promise<void> {
  await api.post('/api/auth/change-password/', payload)
}
