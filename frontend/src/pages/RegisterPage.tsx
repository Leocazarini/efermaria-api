import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { register } from '../api/auth'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { toTitleCase } from '../lib/format'
import type { AxiosError } from 'axios'

export function RegisterPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '',
    password: '', password_confirm: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!authLoading && isAuthenticated) return <Navigate to="/" replace />

  function set(k: keyof typeof form, v: string) {
    setForm(p => ({ ...p, [k]: v }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const username = form.username.trim().toLowerCase()
    if (username.length < 3) {
      setError('O usuário deve ter ao menos 3 caracteres.')
      return
    }
    if (!/^[a-z0-9._-]+$/.test(username)) {
      setError('O usuário só pode conter letras minúsculas, números, ponto, hífen e underscore.')
      return
    }
    if (form.password.length < 8) {
      setError('A senha deve ter ao menos 8 caracteres.')
      return
    }
    if (form.password !== form.password_confirm) {
      setError('As senhas não conferem.')
      return
    }
    setError('')
    setIsSubmitting(true)
    try {
      await register({
        username:         form.username.trim().toLowerCase(),
        email:            form.email.trim().toLowerCase(),
        first_name:       toTitleCase(form.first_name),
        last_name:        toTitleCase(form.last_name),
        password:         form.password,
        password_confirm: form.password_confirm,
      })
      setSuccess(true)
    } catch (err) {
      const e = err as AxiosError<Record<string, string[]>>
      const data = e.response?.data
      if (data && typeof data === 'object') {
        const msg = Object.entries(data)
          .map(([, errs]) => (Array.isArray(errs) ? errs[0] : errs))
          .join(' ')
        setError(msg)
      } else {
        setError('Erro ao criar conta. Tente novamente.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center bg-brand-700 p-12">
        <div className="max-w-xs text-center text-white">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-white/20 backdrop-blur-sm ring-1 ring-white/30">
            <svg className="h-10 w-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.25 4.533A9.707 9.707 0 0 0 6 3a9.735 9.735 0 0 0-3.25.555.75.75 0 0 0-.5.707v14.25a.75.75 0 0 0 1 .707A8.237 8.237 0 0 1 6 18.75c1.995 0 3.823.707 5.25 1.886V4.533ZM12.75 20.636A8.214 8.214 0 0 1 18 18.75c.966 0 1.89.166 2.75.47a.75.75 0 0 0 1-.708V4.262a.75.75 0 0 0-.5-.707A9.735 9.735 0 0 0 18 3a9.707 9.707 0 0 0-5.25 1.533v16.103Z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold">Enfermaria</h1>
          <p className="mt-2 text-brand-200 leading-relaxed">
            Crie sua conta para acessar o sistema de gestão escolar
          </p>
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex flex-1 flex-col items-center justify-center px-5 py-12">
        <div className="w-full max-w-sm">

          {/* Mobile logo */}
          <div className="mb-8 flex flex-col items-center lg:hidden">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-600 shadow-float">
              <svg className="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.25 4.533A9.707 9.707 0 0 0 6 3a9.735 9.735 0 0 0-3.25.555.75.75 0 0 0-.5.707v14.25a.75.75 0 0 0 1 .707A8.237 8.237 0 0 1 6 18.75c1.995 0 3.823.707 5.25 1.886V4.533ZM12.75 20.636A8.214 8.214 0 0 1 18 18.75c.966 0 1.89.166 2.75.47a.75.75 0 0 0 1-.708V4.262a.75.75 0 0 0-.5-.707A9.735 9.735 0 0 0 18 3a9.707 9.707 0 0 0-5.25 1.533v16.103Z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Enfermaria</h1>
            <p className="mt-1 text-sm text-slate-500">Sistema de gestão escolar</p>
          </div>

          {success ? (
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100">
                <svg className="h-8 w-8 text-brand-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Conta criada!</h2>
                <p className="mt-1 text-sm text-slate-500 leading-relaxed">
                  Seu cadastro está pendente de aprovação por um administrador.<br />
                  Você receberá acesso após a aprovação.
                </p>
              </div>
              <Link
                to="/login"
                className="mt-2 text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                Voltar para o login
              </Link>
            </div>
          ) : (
            <>
              <div className="hidden lg:block mb-8">
                <h2 className="text-2xl font-bold text-slate-900">Criar conta</h2>
                <p className="mt-1 text-sm text-slate-500">Preencha os dados para solicitar acesso.</p>
              </div>

              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Nome *"
                    placeholder="João"
                    value={form.first_name}
                    onChange={e => set('first_name', e.target.value)}
                    onBlur={e => set('first_name', toTitleCase(e.target.value))}
                    disabled={isSubmitting}
                    maxLength={50}
                    required
                  />
                  <Input
                    label="Sobrenome *"
                    placeholder="Silva"
                    value={form.last_name}
                    onChange={e => set('last_name', e.target.value)}
                    onBlur={e => set('last_name', toTitleCase(e.target.value))}
                    disabled={isSubmitting}
                    maxLength={50}
                    required
                  />
                </div>

                <Input
                  label="Usuário *"
                  placeholder="joao.silva"
                  autoComplete="username"
                  value={form.username}
                  onChange={e => set('username', e.target.value)}
                  onBlur={e => set('username', e.target.value.trim().toLowerCase())}
                  disabled={isSubmitting}
                  maxLength={150}
                  minLength={3}
                  hint="Apenas letras minúsculas, números, ponto, hífen e underscore."
                  required
                />

                <Input
                  label="E-mail *"
                  type="email"
                  placeholder="joao@exemplo.com"
                  autoComplete="email"
                  value={form.email}
                  onChange={e => set('email', e.target.value)}
                  onBlur={e => set('email', e.target.value.trim().toLowerCase())}
                  disabled={isSubmitting}
                  maxLength={254}
                  required
                />

                <div className="flex flex-col gap-1.5">
                  <label className="text-sm font-medium text-slate-700">Senha *</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Mínimo 8 caracteres"
                      autoComplete="new-password"
                      value={form.password}
                      onChange={e => set('password', e.target.value)}
                      disabled={isSubmitting}
                      minLength={8}
                      maxLength={128}
                      required
                      className="w-full rounded-xl border border-slate-200 bg-white px-3.5 pr-11 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 transition-all focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-400 disabled:bg-slate-50"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      {showPassword ? (
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                        </svg>
                      ) : (
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                <Input
                  label="Confirmar senha *"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Repita a senha"
                  autoComplete="new-password"
                  value={form.password_confirm}
                  onChange={e => set('password_confirm', e.target.value)}
                  disabled={isSubmitting}
                  maxLength={128}
                  required
                />

                {error && (
                  <div className="flex items-center gap-2 rounded-xl bg-red-50 border border-red-200 px-4 py-3">
                    <svg className="h-4 w-4 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm font-medium text-red-700">{error}</p>
                  </div>
                )}

                <Button type="submit" fullWidth size="lg" isLoading={isSubmitting} className="mt-1">
                  Criar conta
                </Button>

                <p className="text-center text-sm text-slate-500">
                  Já tem conta?{' '}
                  <Link to="/login" className="font-semibold text-brand-600 hover:text-brand-700">
                    Entrar
                  </Link>
                </p>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
