import React, { useState, useEffect } from 'react'
import { kpiFormulasApi } from '../../api'
import { Button, Modal, Select, Input } from '../../components/ui'
import toast from 'react-hot-toast'

// Formula templates 
const TEMPLATES = [
  {
    value:       'higher',
    label:       'Higher is Better',
    description: 'Score increases as actual value gets closer to or exceeds target',
    example:     'Bug Resolution Rate, Sales Target, Customer Satisfaction',
    expression:  '(actual / target) * 100',
    requires:    'target (max_threshold)',
  },
  {
    value:       'lower',
    label:       'Lower is Better',
    description: 'Score increases the lower the actual value is',
    example:     'Response Time, System Downtime, Review Time',
    expression:  '((max_threshold - actual) / (max_threshold - min_threshold)) * 100',
    requires:    'min_threshold and max_threshold',
  },
  {
    value:       'task',
    label:       'Task Completion',
    description: 'Full score if target is met, zero if not',
    example:     'Project Delivery, Training Completion, Policy Compliance',
    expression:  '100 if actual >= target else 0',
    requires:    'target (max_threshold)',
  },
  {
    value:       'progress',
    label:       'Progress Above Minimum',
    description: 'Score based on how far above the minimum acceptable level you performed',
    example:     'Sales with minimum quota, Satisfaction with minimum floor',
    expression:  '((actual - min_threshold) / (target - min_threshold)) * 100',
    requires:    'min_threshold and target (max_threshold)',
  },
  {
    value:       'custom',
    label:       'Advanced Custom Formula',
    description: 'Write your own formula for complex measurement needs',
    example:     'Complex KPIs requiring special calculation',
    expression:  null,
    requires:    'Your own variables',
  },
]

const EMPTY_FORM = {
  kpi_uuid:                    '',
  formula_template:            'higher',
  formula_expression:          '(actual / target) * 100',
  data_source:                 '',
  outstanding_threshold:       '',
  good_threshold:              '',
  satisfactory_threshold:      '',
  needs_improvement_threshold: '',
}

export default function KpiFormulaModal({ open, onClose, editTarget, kpis, preselectedKpiUuid, onSuccess }) {
  const [form,   setForm]   = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setForm(editTarget ? {
      kpi_uuid:                    editTarget.kpi_uuid                    || preselectedKpiUuid || '',
      formula_template:            editTarget.formula_template            || 'higher',
      formula_expression:          editTarget.formula_expression          || '',
      data_source:                 editTarget.data_source                 || '',
      outstanding_threshold:       editTarget.outstanding_threshold       ?? '',
      good_threshold:              editTarget.good_threshold              ?? '',
      satisfactory_threshold:      editTarget.satisfactory_threshold      ?? '',
      needs_improvement_threshold: editTarget.needs_improvement_threshold ?? '',
    } : { ...EMPTY_FORM, kpi_uuid: preselectedKpiUuid || '' })
  }, [editTarget, open, preselectedKpiUuid])

  const set = (field) => (e) => setForm(prev => ({ ...prev, [field]: e.target.value }))

  const handleTemplateChange = (templateValue) => {
    const template = TEMPLATES.find(t => t.value === templateValue)
    setForm(prev => ({
      ...prev,
      formula_template:   templateValue,
      formula_expression: template?.expression || '',
    }))
  }

  const selectedTemplate = TEMPLATES.find(t => t.value === form.formula_template)
  const isCustom         = form.formula_template === 'custom'

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.kpi_uuid)           return toast.error('Please select a KPI')
    if (!form.formula_expression) return toast.error('Formula expression is required')

    const payload = {
      kpi_uuid:           form.kpi_uuid,
      formula_expression: form.formula_expression,
      formula_template:   form.formula_template,
    }
    if (form.data_source)                 payload.data_source                 = form.data_source
    if (form.outstanding_threshold)       payload.outstanding_threshold       = form.outstanding_threshold
    if (form.good_threshold)              payload.good_threshold              = form.good_threshold
    if (form.satisfactory_threshold)      payload.satisfactory_threshold      = form.satisfactory_threshold
    if (form.needs_improvement_threshold) payload.needs_improvement_threshold = form.needs_improvement_threshold

    setSaving(true)
    try {
      editTarget
        ? await kpiFormulasApi.update(editTarget.uuid, payload)
        : await kpiFormulasApi.create(payload)
      toast.success(editTarget ? 'Formula updated' : 'Formula created')
      onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error || err.response?.data?.message || 'Something went wrong')
    } finally {
      setSaving(false)
    }
  }

  const kpiLocked = !!preselectedKpiUuid || !!editTarget

  return (
    <Modal open={open} onClose={onClose} title={editTarget ? 'Edit Formula' : 'Add Formula'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">

        {/* KPI selector */}
        <Select label="KPI *" value={form.kpi_uuid} onChange={set('kpi_uuid')} disabled={kpiLocked}>
          <option value="">— Select KPI —</option>
          {kpis.map(k => <option key={k.uuid} value={k.uuid}>{k.kpi_name}</option>)}
        </Select>

        {/* ── Template selector */}
        <div>
          <label className="label">How should this KPI be scored? *</label>
          <div className="space-y-2 mt-1">
            {TEMPLATES.map(t => (
              <div
                key={t.value}
                onClick={() => handleTemplateChange(t.value)}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  form.formula_template === t.value
                    ? 'border-brand-500/40 bg-brand-500/10'
                    : 'border-surface-border hover:border-surface-border/80 hover:bg-surface-muted'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <div className={`w-3.5 h-3.5 rounded-full border-2 flex-shrink-0 ${
                    form.formula_template === t.value
                      ? 'border-brand-400 bg-brand-400'
                      : 'border-text-muted'
                  }`} />
                  <span className={`text-sm font-medium ${
                    form.formula_template === t.value ? 'text-brand-400' : 'text-text-primary'
                  }`}>
                    {t.label}
                  </span>
                </div>
                <p className="text-xs text-text-muted ml-5">{t.description}</p>
                <p className="text-xs text-text-muted ml-5 mt-0.5">
                  <span className="text-text-secondary">Example:</span> {t.example}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Formula display */}
        {selectedTemplate && (
          <div>
            <label className="label">
              {isCustom ? 'Formula Expression *' : 'Generated Formula (read only)'}
            </label>

            {isCustom ? (
              <>
                <input
                  className="input font-mono text-sm"
                  value={form.formula_expression}
                  onChange={set('formula_expression')}
                  placeholder="e.g. (actual / target) * 100"
                />
                <div className="mt-2 bg-surface-muted rounded-lg p-3">
                  <p className="text-xs text-text-muted mb-2">Available variables:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {['actual', 'target', 'weight', 'min_threshold', 'max_threshold'].map(v => (
                      <code key={v} className="text-xs bg-brand-500/10 text-brand-400 border border-brand-500/20 px-2 py-0.5 rounded">
                        {v}
                      </code>
                    ))}
                  </div>
                  <p className="text-xs text-text-muted mt-2">
                    Note: scores are automatically clamped between 0 and 100
                  </p>
                </div>
              </>
            ) : (
              <div className="bg-surface-muted border border-surface-border rounded-lg p-3">
                <code className="text-sm text-brand-400 font-mono">
                  {selectedTemplate.expression}
                </code>
                <p className="text-xs text-text-muted mt-2">
                  Requires: <span className="text-text-secondary">{selectedTemplate.requires}</span>
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Scores are automatically clamped between 0 and 100
                </p>
              </div>
            )}
          </div>
        )}

        {/* Data source */}
        <Input
          label="Data Source"
          value={form.data_source}
          onChange={set('data_source')}
          placeholder="e.g. manual_entry, jira_api"
        />

        {/* Rating thresholds */}
        <div>
          <p className="text-xs text-text-muted pb-2 uppercase tracking-wide">
            Rating Thresholds (optional) — minimum score required for each rating
          </p>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Outstanding ≥"       type="number" step="0.01" value={form.outstanding_threshold}       onChange={set('outstanding_threshold')}       placeholder="90" />
            <Input label="Good ≥"              type="number" step="0.01" value={form.good_threshold}              onChange={set('good_threshold')}              placeholder="75" />
            <Input label="Satisfactory ≥"      type="number" step="0.01" value={form.satisfactory_threshold}      onChange={set('satisfactory_threshold')}      placeholder="60" />
            <Input label="Needs Improvement ≥" type="number" step="0.01" value={form.needs_improvement_threshold} onChange={set('needs_improvement_threshold')} placeholder="40" />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={saving}>{editTarget ? 'Save Changes' : 'Add Formula'}</Button>
        </div>

      </form>
    </Modal>
  )
}