import axiosInstance from '@/api/axiosInstance'

export const getDepartments    = ()           => axiosInstance.get('/org/all_departments/')
export const createDepartment  = (data)       => axiosInstance.post('/org/create_department/', data)
export const updateDepartment  = (uuid, data) => axiosInstance.put(`/org/update_department/${uuid}/`, data)
export const deleteDepartment  = (uuid)       => axiosInstance.delete(`/org/delete_department/${uuid}/`)

export const getTeams          = ()           => axiosInstance.get('/org/all_teams/')
export const createTeam        = (data)       => axiosInstance.post('/org/create_team/', data)
export const updateTeam        = (uuid, data) => axiosInstance.put(`/org/update_team/${uuid}/`, data)
export const deleteTeam        = (uuid)       => axiosInstance.delete(`/org/delete_team/${uuid}/`)