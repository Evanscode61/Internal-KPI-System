export default function DeleteModal({ name, onClose, onConfirm, loading, error }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-sm bg-[#1a1d27] border border-white/10 rounded-2xl shadow-2xl p-6 flex flex-col gap-5">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center text-2xl">
            🗑️
          </div>
          <h2 className="text-white font-semibold text-base">Confirm Delete</h2>
          <p className="text-slate-400 text-sm">
            Are you sure you want to delete{" "}
            <span className="text-white font-semibold">{name}</span>?
          </p>
          <p className="text-slate-600 text-xs">This action cannot be undone.</p>
        </div>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-400 text-sm text-center">
            {error}
          </div>
        )}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-lg border border-white/10 text-slate-300 text-sm hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {loading ? "Deleting…" : "Yes, Delete"}
          </button>
        </div>
      </div>
    </div>
  )
}