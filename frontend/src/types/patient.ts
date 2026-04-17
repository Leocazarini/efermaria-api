export type PatientType = 'student' | 'employee' | 'visitor'

export interface ClassGroup {
  id: number
  name: string
  segment: string
  director: string
}

export interface StudentInfo {
  allergies: string
  patient_notes: string
}

export interface Student {
  id: string
  name: string
  age: number
  gender: string
  email: string
  registry: string
  class_group: ClassGroup
  birth_date: string
  father_name: string
  father_phone: string
  mother_name: string
  mother_phone: string
  info: StudentInfo | null
}

export interface Department {
  id: number
  name: string
  director: string
}

export interface EmployeeInfo {
  allergies: string
  patient_notes: string
}

export interface Employee {
  id: string
  name: string
  age: number
  gender: string
  email: string
  registry: string
  department: Department
  position: string
  birth_date: string
  info: EmployeeInfo | null
}

export interface Visitor {
  id: number
  name: string
  age: number
  gender: string
  email: string
  relationship: string
  allergies: string | null
  patient_notes: string | null
}

export type Patient = Student | Employee | Visitor
