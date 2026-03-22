const inputClass = "w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30 transition-all"

export function Input({ label, error, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
          {label}
        </label>
      )}
      <input className={inputClass} {...props} />
      {error && <p className="text-red-400 text-xs">{error}</p>}
    </div>
  )
}

export function Select({ label, error, children, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
          {label}
        </label>
      )}
      <select className={inputClass} {...props}>
        {children}
      </select>
      {error && <p className="text-red-400 text-xs">{error}</p>}
    </div>
  )
}