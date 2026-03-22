const RATING_CONFIG = {
  outstanding:       { text: "text-emerald-400", label: "Outstanding" },
  good:              { text: "text-blue-400",    label: "Good" },
  satisfactory:      { text: "text-violet-400",  label: "Satisfactory" },
  needs_improvement: { text: "text-amber-400",   label: "Needs Improvement" },
  poor:              { text: "text-red-400",      label: "Poor" },
}

export default function RatingBadge({ rating }) {
  if (!rating) return <span className="text-slate-600 text-xs italic">No data</span>
  const cfg = RATING_CONFIG[rating] || { text: "text-slate-400", label: rating }
  return (
    <span className={`text-xs font-medium capitalize ${cfg.text}`}>
      {cfg.label || rating}
    </span>
  )
}