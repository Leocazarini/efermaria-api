export interface AppointmentBase {
  id: number
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  notes: string
  revaluation: boolean
  created_at: string
  updated_at: string
}

export interface StudentAppointment extends AppointmentBase {
  student_id: number
  current_class: string
  contact_parents: boolean
  allergies: string
  patient_notes: string
}

export interface EmployeeAppointment extends AppointmentBase {
  employee_id: number
  allergies: string
  patient_notes: string
}

export interface VisitorAppointment extends AppointmentBase {
  visitor: {
    name: string
    age: number
    gender: string
    email: string
    relationship: string
    allergies: string
    patient_notes: string
  }
}

export interface StudentAppointmentCreate {
  student_id: string
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  current_class: string
  contact_parents: boolean
  notes?: string
  revaluation: boolean
  allergies?: string
  patient_notes?: string
}

export interface EmployeeAppointmentCreate {
  employee_id: string
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  notes?: string
  revaluation: boolean
  allergies?: string
  patient_notes?: string
}

export interface VisitorAppointmentCreate {
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  notes?: string
  revaluation: boolean
  visitor: {
    name: string
    age: number
    gender: string
    email: string
    relationship?: string
    allergies?: string
    patient_notes?: string
  }
}

export interface Stats {
  total_current_year: number
  total_today: number
  nurses: Array<{ nurse: string; count: number }>
  monthly_counts: Array<{ month: number; count: number }>
  recent_appointments: ReportAppointment[]
}

export interface ReportAppointment {
  id: number
  patient_type: string
  patient_name: string
  additional_info_label: string
  additional_info: string
  age: number
  gender: string
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  notes: string | null
  revaluation: boolean
  contact_parents: boolean | string
  current_class: string
}

export interface PendingRevaluation {
  id: number
  appointment_type: 'student' | 'employee' | 'visitor'
  patient_id: number
  patient_name: string
  infirmary: string
  nurse: string
  date: string
  reason: string
  notes: string | null
  visitor_data?: {
    name: string
    age: number
    gender: string
    email: string
    relationship: string
    allergies: string
    patient_notes: string
  }
}

export interface ReportFilters {
  date_begin: string
  date_end: string
  infirmaries?: string[]
  search?: string
}
