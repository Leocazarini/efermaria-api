import { api } from '../lib/axios'
import type { Student, Employee, Visitor } from '../types/patient'

export async function searchStudents(name: string): Promise<Student[]> {
  const { data } = await api.get<Student[]>('/api/v1/patients/students/', {
    params: { name },
  })
  return data
}

export async function getStudent(id: number): Promise<Student> {
  const { data } = await api.get<Student>(`/api/v1/patients/students/${id}/`)
  return data
}

export async function searchEmployees(name: string): Promise<Employee[]> {
  const { data } = await api.get<Employee[]>('/api/v1/patients/employees/', {
    params: { name },
  })
  return data
}

export async function getEmployee(id: number): Promise<Employee> {
  const { data } = await api.get<Employee>(`/api/v1/patients/employees/${id}/`)
  return data
}

export async function searchVisitors(name: string): Promise<Visitor[]> {
  const { data } = await api.get<Visitor[]>('/api/v1/patients/visitors/', {
    params: { name },
  })
  return data
}

export async function getVisitor(id: number): Promise<Visitor> {
  const { data } = await api.get<Visitor>(`/api/v1/patients/visitors/${id}/`)
  return data
}
