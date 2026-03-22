export default function Toast({ message }) {
  if (!message) return null
  return (
    <div className="fixed bottom-6 right-6 z-50 bg-emerald-600 text-white text-sm font-medium px-5 py-3 rounded-xl shadow-lg">
      ✓ {message}
    </div>
  )
}