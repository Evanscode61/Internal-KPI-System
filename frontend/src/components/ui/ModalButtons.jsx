export default function ModalButtons({ onCancel, onConfirm, loading, confirmLabel = "Save", cancelLabel = "Cancel" }) {
  return (
    <div className="flex gap-3 pt-1">
      <button
        onClick={onCancel}
        className="flex-1 py-2.5 rounded-lg border border-white/10 text-slate-300 text-sm hover:bg-white/5 transition-colors"
      >
        {cancelLabel}
      </button>
      <button
        onClick={onConfirm}
        disabled={loading}
        className="flex-1 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium transition-colors"
      >
        {loading ? "Saving…" : confirmLabel}
      </button>
    </div>
  )
}