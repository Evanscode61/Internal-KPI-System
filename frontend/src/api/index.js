import api from './axiosInstance'

// ── AUTH ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login:        (data)          => api.post('/auth/login/', data),
  logout:       (refresh_token) => api.post('/auth/logout/', { refresh_token }),
  refresh:      (refresh_token) => api.post('/auth/refresh/', { refresh_token }),
  register:     (data)          => api.post('/auth/register_user/', data),
  requestOtp:   (data)          => api.post('/auth/otp/request/', data),
  resetPassword:(data)          => api.post('/auth/reset_password/', data),
  getProfile:   (uuid)          => api.get(`/auth/user/profile/${uuid}/`),
}

// ── USERS ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  list:       ()             => api.get('/auth/list_users/'),
  create:     (data)         => api.post('/auth/create_user/', data),
  update:     (uuid, data)   => api.patch(`/auth/update_user/${uuid}/`, data),
  delete:     (uuid)         => api.delete(`/auth/delete_user/${uuid}/`),
  profile:    (uuid)         => api.get(`/auth/user/profile/${uuid}/`),
  assignRole: (data)         => api.post('/auth/role/assign/', data),
}

// ── ROLES ─────────────────────────────────────────────────────────────────────
export const rolesApi = {
  list:   ()             => api.get('/auth/role/list/'),
  create: (data)         => api.post('/auth/role/create/', data),
  delete: (name)         => api.delete(`/auth/role/delete/${name}/`),
  update: (name, data)   => api.put(`/auth/role/update/${name}/`, data),
}

// ── KPI DEFINITIONS ───────────────────────────────────────────────────────────
export const kpiDefinitionsApi = {
  list:   ()             => api.get('/kpis/kpi_definition/list_all/'),
  get:    (uuid)         => api.get(`/kpis/kpi_definition/get_kpi/${uuid}/`),
  create: (data)         => api.post('/kpis/kpi_definition/create/', data),
  update: (uuid, data)   => api.patch(`/kpis/kpi_definition/update/${uuid}/`, data),
  delete: (uuid)         => api.delete(`/kpis/kpi_definition/delete/${uuid}/`),
}

// ── KPI ASSIGNMENTS ───────────────────────────────────────────────────────────
export const kpiAssignmentsApi = {
  list:   ()             => api.get('/kpis/kpi_assignment/get_all/'),
  create: (data)         => api.post('/kpis/kpi_assignment/create/', data),
  update: (uuid, data)   => api.patch(`/kpis/kpi_assignment/update/${uuid}/`, data), 
  delete: (uuid) => api.delete(`/kpis/kpi_assignment/delete/${uuid}/`),
}

// ── KPI FORMULAS ──────────────────────────────────────────────────────────────
export const kpiFormulasApi = {
  getByKpi: (kpiUuid)       => api.get(`/kpis/kpi_formula/get_formula/${kpiUuid}/`),
  create:   (data)          => api.post('/kpis/kpi_formula/create/', data),
  update:   (uuid, data)    => api.patch(`/kpis/kpi_formula/update/${uuid}/`, data),
  delete:   (uuid)          => api.delete(`/kpis/kpi_formula/delete/${uuid}/`),
}

// ── KPI RESULTS ───────────────────────────────────────────────────────────────
export const kpiResultsApi = {
  list:       ()           => api.get('/kpis/kpi_results/get_all/'),
  get:        (uuid)       => api.get(`/kpis/kpi_results/get_one/${uuid}/`),
  submit:     (data)       => api.post('/kpis/kpi_results/submit/', data),
  update:     (uuid, data) => api.patch(`/kpis/kpi_results/update/${uuid}/`, data),
  review:     (uuid, data) => api.patch(`/kpis/kpi_results/review/${uuid}/`, data),
  exportBlob: ()           => api.get('/kpis/kpi_results/export_csv/', { responseType: 'blob' }),
  delete :    (uuid)       => api.delete(`/kpis/kpi_results/delete/${uuid}/`),
}

// ── ORGANIZATION ──────────────────────────────────────────────────────────────
export const departmentsApi = {
  list:   ()             => api.get('/org/all_departments/'),
  get:    (uuid)         => api.get(`/org/get_department/${uuid}/`),
  create: (data)         => api.post('/org/create_department/', data),
  update: (uuid, data)   => api.patch(`/org/update_department/${uuid}/`, data),
  delete: (uuid)         => api.delete(`/org/delete_department/${uuid}/`),
}

export const teamsApi = {
  list:       ()             => api.get('/org/all_teams/'),
  get:        (uuid)         => api.get(`/org/get_team/${uuid}/`),
  create:     (data)         => api.post('/org/create_team/', data),
  update:     (uuid, data)   => api.patch(`/org/update_team/${uuid}/`, data),
  delete:     (uuid)         => api.delete(`/org/delete_team/${uuid}/`),
  assignUser: (data)         => api.post('/org/assign-user_team/', data),
}

// ── PERFORMANCE ───────────────────────────────────────────────────────────────
export const performanceApi = {
  generateSummary: (data)   => api.post('/performance/performance/summaries/generate/', data),
  listSummaries:   ()       => api.get('/performance/performance/summaries/get_all/'),
  getSummary:      (uuid)   => api.get(`/performance/performance/summaries/${uuid}/`),
  exportCsv:       ()       => api.get('/performance/performance/summaries/export/csv/', { responseType: 'blob' }),
  dashboard:       (params) => api.get('/performance/dashboard/', { params }),
    deleteSummary: (uuid) => api.delete(`/performance/performance/summaries/delete/${uuid}/`),

}

// ── NOTIFICATIONS ─────────────────────────────────────────────────────────────
export const notificationsApi = {
  getUnread:   ()    => api.get('/performance/notifications/get/'),
  getAll:      ()    => api.get('/performance/notifications/all/'),
  markRead:    (id)  => api.patch(`/performance/notifications/${id}/read/`),
  markAllRead: ()    => api.patch('/performance/notifications/read_all/'),
  delete: (id) => api.delete(`/performance/notifications/${id}/delete/`),
}

// ── AUDIT LOGS ────────────────────────────────────────────────────────────────
export const auditApi = {
  list: ()     => api.get('/audit/logs/'),
  get:  (uuid) => api.get(`/audit/logs/${uuid}/`),
}

export const alertsApi = {
  getAll:     ()         => api.get('/performance/alerts/all/'),
  resolve:    (id, data) => api.patch(`/performance/alerts/${id}/resolve/`, data),
  resolveAll: ()         => api.patch('/performance/alerts/resolve_all/'),
}