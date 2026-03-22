export default function ApiError({ message }) {
  if (!message) return null
  return (
    <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-400 text-sm">
      {message}
    </div>
  )
}