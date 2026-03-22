export default function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop — click outside to close */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-md bg-[#1a1d27] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header with title and X button */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <h2 className="text-white font-semibold text-base">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl leading-none">✕</button>
        </div>

        {/* Scrollable content — scrollbar hidden */}
        <div className="px-6 py-5 flex flex-col gap-4 max-h-[80vh] overflow-y-auto
          [&::-webkit-scrollbar]:w-1
          [&::-webkit-scrollbar-track]:bg-transparent
          [&::-webkit-scrollbar-thumb]:bg-white/10
          [&::-webkit-scrollbar-thumb]:rounded-full
          hover:[&::-webkit-scrollbar-thumb]:bg-white/20">
          {children}
        </div>

      </div>
    </div>
  )
}