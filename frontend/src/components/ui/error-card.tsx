import { RefreshCcw } from "lucide-react"

export function ErrorCard({ onRetry, message = "Failed to load data" }: { onRetry: () => void, message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-6 bg-panel border border-zinc-800 rounded-lg shadow-md h-full min-h-[120px]">
      <div className="text-red-400 text-sm font-medium mb-3">{message}</div>
      <button 
        onClick={onRetry}
        className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs rounded transition-colors"
      >
        <RefreshCcw className="w-3 h-3" />
        Retry
      </button>
    </div>
  )
}
