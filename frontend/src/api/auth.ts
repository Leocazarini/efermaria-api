import { api } from '../lib/axios'
import type { LoginCredentials, TokenPair, UserProfile, AdminUser } from '../types/auth'

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

export async function listUsers(): Promise<AdminUser[]> {
  const { data } = await api.get<AdminUser[]>('/api/auth/users/')
  return data
}

export async function approveUser(id: number): Promise<void> {
  await api.post(`/api/auth/users/${id}/approve/`)
}

export async function patchUser(id: number, payload: { is_active?: boolean; is_staff?: boolean }): Promise<AdminUser> {
  const { data } = await api.patch<AdminUser>(`/api/auth/users/${id}/`, payload)
  return data
}

export async function deleteUser(id: number): Promise<void> {
  await api.delete(`/api/auth/users/${id}/`)
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
