import { useState } from 'react'
import DeleteModal from '@/components/ui/DeleteModal'
import { deleteUser } from '@/services/userService'

export default function UserDeleteModal({ user, onClose, onDeleted }) {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const handleDelete = async () => {
    setLoading(true)
    setError('')
    try {
      await deleteUser(user.uuid)
      onDeleted(user.username)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete user')
      setLoading(false)
    }
  }

  return (
    <DeleteModal
      name={user.username}
      onClose={onClose}
      onConfirm={handleDelete}
      loading={loading}
      error={error}
    />
  )
}