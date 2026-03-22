import React, { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { kpiResultsApi } from '../../api'
import { Modal, Input, Button } from '../../components/ui'
import toast from 'react-hot-toast'

export default function SubmitResultModal({ target, onClose }) {
  const queryClient = useQueryClient()
  const [actualValue, setActualValue] = useState('')

  useEffect(() => {
    if (target) setActualValue('')
  }, [target])

  const mutation = useMutation({
    mutationFn: (payload) => kpiResultsApi.submit(payload),
    onSuccess: () => {
      toast.success(target?.isResubmit ? 'Result resubmitted successfully' : 'Result submitted successfully')
      queryClient.invalidateQueries({ queryKey: ['kpi-results'] })
      onClose()
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || err.response?.data?.error || 'Submission failed')
    },
  })

  const handleSubmit = () => {
    if (!actualValue) return toast.error('Please enter an actual value')
    mutation.mutate({
      assignment_uuid: target.assignment_uuid,
      actual_value: actualValue,
    })
  }

  return (
    <Modal
      open={!!target}
      onClose={onClose}
      title={target?.isResubmit ? 'Resubmit KPI Result' : 'Submit KPI Result'}
      size="sm"
    >
      {target && (
        <div className="space-y-4">
          <p className="text-sm text-text-secondary">
            {target?.isResubmit
              ? 'Your previous submission was rejected. Enter a new value to resubmit.'
              : 'Enter your actual value. The score will be calculated automatically.'
            }
          </p>
          <Input
            label="Actual Value"
            type="number"
            value={actualValue}
            onChange={e => setActualValue(e.target.value)}
            placeholder="e.g. 85"
          />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={onClose} disabled={mutation.isPending}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} loading={mutation.isPending}>
              {target?.isResubmit ? 'Resubmit' : 'Submit Result'}
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}