import axiosInstance from '@/api/axiosInstance'

export const getUsers    = ()           => axiosInstance.get('/auth/list_users/')
export const createUser  = (data)       => axiosInstance.post('/auth/create_user/', data)
export const updateUser  = (uuid, data) => axiosInstance.patch(`/auth/update_user/${uuid}/`, data)
export const deleteUser  = (uuid)       => axiosInstance.delete(`/auth/delete_user/${uuid}/`)
export const assignRole  = (data)       => axiosInstance.post('/auth/role/assign/', data)
export const assignTeam  = (data)       => axiosInstance.post('/org/assign-user_team/', data)
export const getRoles    = ()           => axiosInstance.get('/auth/role/list/')
export const getDepts    = ()           => axiosInstance.get('/org/all_departments/')
export const getTeams    = ()           => axiosInstance.get('/org/all_teams/')