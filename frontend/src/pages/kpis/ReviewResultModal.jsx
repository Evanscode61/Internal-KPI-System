import React, { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { kpiResultsApi } from '../../api'
import { Modal, Button, Textarea, RatingBadge, DetailRow } from '../../components/ui'
import { Check, X } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ReviewResultModal({ target, onClose }) {
  const queryClient = useQueryClient()
  const [comment, setComment] = useState('')

  useEffect(() => {
    if (target) setComment('')
  }, [target])

  const mutation = useMutation({
    mutationFn: ({ status }) =>
      kpiResultsApi.review(target.uuid, { approval_status: status, manager_comment: comment }),
    onSuccess: (_, { status }) => {
      toast.success(`Result ${status} successfully`)
      queryClient.invalidateQueries({ queryKey: ['kpi-results'] })
      onClose()
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || err.response?.data?.error || 'Review failed')
    },
  })

  return (
    <Modal open={!!target} onClose={onClose} title="Review Submission" size="sm">
      {target && (
        <div className="space-y-4">
          <div className="bg-surface-muted rounded-lg p-4 space-y-3">
            <DetailRow label="KPI"      value={target.kpi_name} />
            <DetailRow label="Employee" value={target.submitted_by || '—'} />
            <DetailRow label="Target"   value={`${target.target ?? '—'} ${target.measurement_type || ''}`} />
            <DetailRow label="Actual"   value={`${parseFloat(target.actual_value).toFixed(1)} ${target.measurement_type || ''}`} />
            <DetailRow label="Score"    value={target.calculated_score ? `${parseFloat(target.calculated_score).toFixed(1)}%` : '—'} />
            <div className="flex items-center justify-between">
              <span className="text-sm text-text-secondary">Rating</span>
              <RatingBadge rating={target.rating} />
            </div>
          </div>
          <Textarea
            label="Comment (optional)"
            value={comment}
            onChange={e => setComment(e.target.value)}
            placeholder="Add feedback for the employee…"
            rows={3}
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={onClose} disabled={mutation.isPending}>Cancel</Button>
            <Button variant="danger" onClick={() => mutation.mutate({ status: 'rejected' })} loading={mutation.isPending}>
              <X size={14} /> Reject
            </Button>
            <Button onClick={() => mutation.mutate({ status: 'approved' })} loading={mutation.isPending}>
              <Check size={14} /> Approve
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}